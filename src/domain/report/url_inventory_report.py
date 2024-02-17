import logging

import pandas as pd

from domain.report.base_report import BaseReport
from model.core.project.models import ProjectModel
from model.core.url.models import UrlModelManager
from model.report.url_inventory_report.models import UrlInventoryReportModelManager, UrlInventoryReportModel

logger = logging.getLogger(__name__)


class UrlInventoryReport(BaseReport):
    _REPORT_NAME = "url_inventory_report"

    def __init__(self, project: ProjectModel):
        super().__init__(project)
        self.url_inventory = None

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
        self._report_base = pd.DataFrame(unique_urls, columns=["BASE_URL"])
        self._export_data["url_inventory_report"] = self.export_manager.get_data("url_inventory_report", urls=unique_urls)

    def _process_data(self) -> None:
        self._report_data = self._report_base.merge(self._export_data["url_inventory_report"], left_on="BASE_URL", right_on="request_url", how="left")

    def _finalize(self) -> None:
        # Drop all columns that start with "BASE_"
        base_columns = [col for col in self._report_data.columns if col.startswith("BASE_")]
        self._report_data.drop(columns=base_columns, inplace=True)

    def _update_db(self) -> None:
        for index, row in self._report_data.iterrows():
            arguments = row.to_dict()
            arguments["project"] = self.project
            UrlInventoryReportModelManager.push(**arguments)
