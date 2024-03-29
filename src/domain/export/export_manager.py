import logging
from typing import Any, Dict, Type

import pandas as pd

from domain.export.base_export import BaseExport
from domain.export.googleanalytics.googleanalytics_months_14_to_0_export import GoogleAnalyticsMonths14To0Export
from domain.export.googlesearchconsole.googleasearchconsole_page_months_16_to_0_export import GoogleSearchConsolePageMonths16To0Export
from domain.export.googlesearchconsole.googleasearchconsole_query_page_months_16_to_1_export import GoogleSearchConsoleQueryPageMonths16To1Export
from domain.export.googlesearchconsole.googleasearchconsole_query_page_months_1_to_0_export import GoogleSearchConsoleQueryPageMonths1To0Export
from domain.export.googlesearchconsole.googleasearchconsole_query_page_weeks_1_to_0_export import GoogleSearchConsoleQueryPageWeeks1To0Export
from domain.export.googlesearchconsole.googleasearchconsole_query_page_weeks_78_to_1_export import GoogleSearchConsoleQueryPageWeeks78To1Export
from domain.export.page.raw_page_data_export import RawPageDataExport
from domain.export.screamingfrog.screamingfrog_list_crawl_export import ScreamingFrogListCrawlExport
from domain.export.screamingfrog.screamingfrog_sitemap_crawl_export import ScreamingFrogSitemapCrawlExport
from domain.export.screamingfrog.screamingfrog_spider_crawl_export import ScreamingFrogSpiderCrawlExport
from domain.export.semrush.semrush_analytics_backlinks_backlinks_domain_export import SemrushAnalyticsBacklinksBacklinksDomainExport
from domain.export.semrush.semrush_analytics_organic_pages_domain_export import SemrushAnalyticsOrganicPagesDomainExport
from domain.export.semrush.semrush_analytics_organic_positions_domain_export import SemrushAnalyticsOrganicPositionsDomainExport
from model.core.project.models import ProjectModel

logger = logging.getLogger(__name__)


class ExportManager:

    AVAILABLE_EXPORTS: Dict[str, Type[BaseExport]] = {
        "url_inventory_report": RawPageDataExport,
        "semrush_analytics_organic_pages_domain": SemrushAnalyticsOrganicPagesDomainExport,
        "semrush_analytics_organic_positions_domain": SemrushAnalyticsOrganicPositionsDomainExport,
        "semrush_analytics_backlinks_backlinks_domain": SemrushAnalyticsBacklinksBacklinksDomainExport,
        "screamingfrog_spider_crawl_export": ScreamingFrogSpiderCrawlExport,
        "screamingfrog_sitemap_crawl_export": ScreamingFrogSitemapCrawlExport,
        "screamingfrog_list_crawl_export": ScreamingFrogListCrawlExport,
        "googleanalytics_months_14_to_0_export": GoogleAnalyticsMonths14To0Export,
        "googleasearchconsole_page_months_16_to_0_export": GoogleSearchConsolePageMonths16To0Export,
        "googleasearchconsole_query_page_months_16_to_1_export": GoogleSearchConsoleQueryPageMonths16To1Export,
        "googleasearchconsole_query_page_months_1_to_0_export": GoogleSearchConsoleQueryPageMonths1To0Export,
        "googleasearchconsole_query_page_weeks_78_to_1_export": GoogleSearchConsoleQueryPageWeeks78To1Export,
        "googleasearchconsole_query_page_weeks_1_to_0_export": GoogleSearchConsoleQueryPageWeeks1To0Export,
        # Add more exports as needed
    }

    def __init__(self, project: ProjectModel):
        self.project = project

    def get_data(self, export_type: str, **kwargs: Any) -> pd.DataFrame:
        # Check if the requested export type is available
        if export_type in self.AVAILABLE_EXPORTS:
            # Instantiate the export class with the project and any additional kwargs
            export_instance = self.AVAILABLE_EXPORTS[export_type](self.project, **kwargs)
            # Run the export
            return export_instance.get_data()
        else:
            raise ValueError(f"Export type '{export_type}' is not available.")
