import hashlib
import logging
import os
from typing import Any

import pandas as pd

from domain.export.base_export import BaseExport
from model.core.project.models import ProjectModel
from operators.browser_operator import BrowserOperator

logger = logging.getLogger(__name__)


class RawPageDataExport(BaseExport):

    _EXPORT_NAME = "page_data"
    _IS_MANUAL = False

    def __init__(self, project: ProjectModel, **kwargs: Any):
        super().__init__(project, **kwargs)
        self.kwargs = kwargs
        self._browser_operator = None

        self.source_dir = os.path.join(project.data_folder, "source")
        os.makedirs(self.source_dir, exist_ok=True)

    @property
    def export_name(self) -> str:
        return self._EXPORT_NAME

    @property
    def is_manual(self) -> bool:
        return self._IS_MANUAL

    def _save_page_sources(self) -> None:
        """Save the page sources to HTML files."""
        for index, row in self._page_sources.iterrows():
            file_path = os.path.join(self.source_dir, row["filename"])

            with open(file_path, "w", encoding="utf-8") as file:
                file.write(row["page_content"])

    def _cleanup(self) -> None:
        pass

    def _prepare(self) -> None:
        self._browser_operator = BrowserOperator()

    def _execute(self) -> None:
        urls = self.kwargs.get("urls", [])
        for url in urls:
            try:
                self._browser_operator.get_page_contents(url)
                response_url = self._browser_operator.driver.current_url

                # Initialize a dictionary to categorize status codes for the specific request URL
                status_codes = {"5xx": [], "4xx": [], "3xx": [], "2xx": []}

                # Inspect all requests and responses
                for request in self._browser_operator.driver.requests:
                    if request.response and request.url == url:  # Filter by request URL
                        code = request.response.status_code
                        category = f"{code // 100}xx"  # Group status codes by their first digit
                        status_codes[category].append(code)

                # Determine the most critical status code for the specific request URL
                relevant_status_code = None
                for category in ["5xx", "4xx", "3xx", "2xx"]:
                    if status_codes[category]:
                        relevant_status_code = max(status_codes[category])  # Choose the "worst" code within the category
                        break

                # Handle cases where the request URL matches the response URL but no status code was found
                if url == response_url and relevant_status_code is None:
                    relevant_status_code = "Unknown"

                # Append data to the DataFrame
                new_row = pd.DataFrame(
                    {
                        "request_url": [url],
                        "status_code": [relevant_status_code],
                        "response_url": [response_url],
                        "page_content": [self._browser_operator.driver.page_source],
                    }
                )
                self._temp_data = pd.concat([self._temp_data, new_row], ignore_index=True)
            except Exception as e:
                logger.error(f"Failed to fetch content for URL {url}: {e}")

    def _finalize(self) -> None:
        self._browser_operator.close_browser()

        filenames = []
        page_sources = []

        for index, row in self._temp_data.iterrows():
            url_hash = hashlib.md5(row["request_url"].encode("utf-8")).hexdigest()
            filename = f"{url_hash}.html"
            filenames.append(filename)

            # Prepare a separate list for page sources to be saved later
            page_sources.append({"filename": filename, "page_content": row["page_content"]})

        # Add the filename column to the main DataFrame
        self._temp_data["page_content_file"] = filenames

        # Drop the page_content column from the main DataFrame
        self._temp_data.drop(columns=["page_content"], inplace=True)

        # Create a new DataFrame for page sources
        self._page_sources = pd.DataFrame(page_sources)
        self._save_page_sources()
