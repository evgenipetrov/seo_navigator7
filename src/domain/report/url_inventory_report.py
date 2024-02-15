from domain.report.base_report import BaseReport
from model.core.project.models import ProjectModel


class UrlInventoryReport(BaseReport):
    def __init__(self, project: ProjectModel):
        super().__init__(project)
        self.url_inventory = None

    def _collect_data(self) -> None:
        self._data_semrush_analytics_organic_pages_domain = self.export_manager.get_data("semrush_analytics_organic_pages_domain")

    def _prepare_data(self) -> None:
        pass

    def _process_data(self) -> None:
        pass

    def _save_data(self) -> None:
        pass
