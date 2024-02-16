import logging

import pandas as pd

from domain.report.base_report import BaseReport
from model.core.project.models import ProjectModel
from model.report.raw_page_data.models import RawPageDataModelManager

logger = logging.getLogger(__name__)


class UrlInventoryReport(BaseReport):
    def __init__(self, project: ProjectModel):
        super().__init__(project)
        self.url_inventory = None

    def _collect_data(self) -> None:
        self._export_data["semrush_analytics_organic_pages_domain"] = self.export_manager.get_data("semrush_analytics_organic_pages_domain")
        self._export_data["semrush_analytics_organic_positions_domain"] = self.export_manager.get_data("semrush_analytics_organic_positions_domain")
        self._export_data["semrush_analytics_backlinks_backlinks_domain"] = self.export_manager.get_data("semrush_analytics_backlinks_backlinks_domain")

    def _prepare_data(self) -> None:
        urls = self._export_data["semrush_analytics_organic_pages_domain"]["URL"].tolist()
        urls.extend(self._export_data["semrush_analytics_organic_positions_domain"]["URL"].tolist())
        urls.extend(self._export_data["semrush_analytics_backlinks_backlinks_domain"]["Target url"].tolist())

        unique_urls = list(set(urls))
        self._report_base = pd.DataFrame(unique_urls, columns=["BASE_URL"])
        self._export_data["raw_page_data"] = self.export_manager.get_data("raw_page_data", urls=unique_urls)

    def _process_data(self) -> None:
        self._report_data = self._report_base.merge(self._export_data["raw_page_data"], left_on="BASE_URL", right_on="request_url", how="left")

    def _finalize(self) -> None:
        # Drop all columns that start with "BASE_"
        base_columns = [col for col in self._report_data.columns if col.startswith("BASE_")]
        self._report_data.drop(columns=base_columns, inplace=True)

    def _save_data(self) -> None:
        for index, row in self._report_data.iterrows():
            arguments = row.to_dict()
            arguments["project"] = self.project
            RawPageDataModelManager.push(**arguments)
