import logging

from domain.export.semrush.base_semrush_export import BaseSemrushExport

logger = logging.getLogger(__name__)


class SemrushAnalyticsBacklinksBacklinksDomainExport(BaseSemrushExport):
    _EXPORT_NAME = "semrush_analytics_backlinks_backlinks_domain"
    _URL_TEMPLATE = "https://www.semrush.com/analytics/backlinks/backlinks/?searchType=domain&q={}"

    @property
    def export_name(self) -> str:
        return self._EXPORT_NAME

    @property
    def url_template(self) -> str:
        return self._URL_TEMPLATE

    def _print_instructions(self) -> None:
        project_url = self.project.website.root_url

        formatted_url = self.url_template.format(project_url)

        formatted_instructions = [
            "1. Open your web browser and navigate to the Semrush URL below.",
            f"2. Navigate to: {formatted_url}",
            "3. Follow the on-screen instructions to export the data.",
            f"4. Save the exported data to: {self.temp_dir}",
        ]

        print("\n".join(formatted_instructions))

    def _prepare(self) -> None:
        self._print_instructions()
