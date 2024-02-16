import logging

from domain.report.base_report import BaseReport
from model.core.project.models import ProjectModel

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
        pass

    def _process_data(self) -> None:
        pass

    def _save_data(self) -> None:
        pass
