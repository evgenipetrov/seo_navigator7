import logging

import pandas as pd

from domain.report.base_report import BaseReport
from model.core.project.models import ProjectModel
from model.core.url.models import UrlModelManager
from model.report.url_inventory_report.models import UrlInventoryReportModel
from operators.dataframe_operator import DataFrameOperator

logger = logging.getLogger(__name__)


class UrlInventoryReport(BaseReport):
    _REPORT_NAME = "url_inventory_report"

    def __init__(self, project: ProjectModel):
        super().__init__(project)

    @property
    def report_name(self) -> str:
        return self._REPORT_NAME

    @property
    def model_class(self) -> UrlInventoryReportModel:
        return UrlInventoryReportModel

    def _collect_data(self) -> None:
        self._export_data["semrush_analytics_organic_pages_domain"] = self.export_manager.get_data("semrush_analytics_organic_pages_domain")
        self._export_data["semrush_analytics_organic_positions_domain"] = self.export_manager.get_data("semrush_analytics_organic_positions_domain")
        self._export_data["semrush_analytics_backlinks_backlinks_domain"] = self.export_manager.get_data("semrush_analytics_backlinks_backlinks_domain")
        self._export_data["screamingfrog_spider_crawl_export"] = self.export_manager.get_data("screamingfrog_spider_crawl_export")
        self._export_data["screamingfrog_sitemap_crawl_export"] = self.export_manager.get_data("screamingfrog_sitemap_crawl_export")
        self._export_data["googleanalytics_months_14_to_0_export"] = self.export_manager.get_data("googleanalytics_months_14_to_0_export")
        self._export_data["googleasearchconsole_page_months_16_to_0_export"] = self.export_manager.get_data("googleasearchconsole_page_months_16_to_0_export")

    def _prepare_data(self) -> None:
        urls = []
        urls.extend(self._export_data["semrush_analytics_organic_pages_domain"]["URL"].tolist())
        urls.extend(self._export_data["semrush_analytics_organic_positions_domain"]["URL"].tolist())
        urls.extend(self._export_data["semrush_analytics_backlinks_backlinks_domain"]["Target url"].tolist())
        urls.extend(self._export_data["screamingfrog_spider_crawl_export"]["Address"].tolist())
        urls.extend(self._export_data["screamingfrog_sitemap_crawl_export"]["Address"].tolist())
        urls.extend(self._export_data["googleanalytics_months_14_to_0_export"]["FULL_ADDRESS"].tolist())
        urls.extend(self._export_data["googleasearchconsole_page_months_16_to_0_export"]["page"].tolist())
        # prepare for final list crawl
        unique_urls = list(set(urls))
        unique_urls = [url for url in unique_urls if not UrlModelManager.is_fragmented(url)]  # drop fragmented urls
        self._export_data["screamingfrog_list_crawl_export"] = self.export_manager.get_data("screamingfrog_list_crawl_export", urls=unique_urls)
        # collect list crawl data
        urls.extend(self._export_data["screamingfrog_list_crawl_export"]["Address"].tolist())
        # set report base
        unique_urls = list(set(urls))
        unique_urls = [url for url in unique_urls if not UrlModelManager.is_fragmented(url)]  # drop fragmented urls
        self._export_data["url_inventory_report"] = self.export_manager.get_data("url_inventory_report", urls=unique_urls)  # Initialize _report_base DataFrame with columns from UrlInventoryReportModel
        model_fields = self.model_class.objects.get_field_names()  # Use your method to get field names
        model_fields.append("BASE_URL")  # Add BASE_URL to the list of columns
        self._report_base = pd.DataFrame(columns=model_fields)
        # Populate BASE_URL column with unique URLs
        self._report_base["BASE_URL"] = pd.Series(unique_urls)

    # def _process_data(self) -> None:
    #     # Merge _report_base with _export_data["url_inventory_report"] on matching URLs
    #     # This merge temporarily combines the data to facilitate the update
    #     merged_df = self._report_base.merge(self._export_data["url_inventory_report"], left_on="BASE_URL", right_on="request_url", how="left", suffixes=("", "_update"))
    #
    #     # Iterate through columns to update _report_base from _export_data["url_inventory_report"]
    #     for col in merged_df.columns:
    #         if col.endswith("_update"):
    #             # Determine the original column name by removing '_update' suffix
    #             original_col = col[:-7]  # '_update' is 7 characters long
    #
    #             # Check if the original column exists in _report_base
    #             if original_col in self._report_base.columns:
    #                 # Update _report_base with values from the merged DataFrame
    #                 # Prefer values from the '_update' column, falling back to the original where '_update' is NaN
    #                 self._report_base[original_col] = merged_df[col].combine_first(merged_df[original_col])
    #
    #     # Note: _report_data is updated with the final _report_base DataFrame
    #     self._report_data = self._report_base.copy()

    def _process_data(self) -> None:
        self._report_base = DataFrameOperator.update_df_from_df(self._report_base, self._export_data["url_inventory_report"], "BASE_URL", "request_url")
        self._report_data = self._report_base.copy()

    def _finalize(self) -> None:
        self._report_data["project"] = self.project
        # Drop all columns that start with "BASE_"
        base_columns = [col for col in self._report_data.columns if col.startswith("BASE_")]
        self._report_data.drop(columns=base_columns, inplace=True)

    def _update_db(self) -> None:
        for index, row in self._report_data.iterrows():
            arguments = row.to_dict()
            self.model_class.objects.push(**arguments)
        logger.info(f"[database updated] {self.project.name}")
