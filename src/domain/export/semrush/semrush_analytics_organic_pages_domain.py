from domain.export.semrush.base_semrush_export import BaseSemrushExport


class SemrushAnalyticsOrganicPagesDomainExport(BaseSemrushExport):
    _EXPORT_NAME = "semrush_analytics_organic_pages_domain"
    _URL_TEMPLATE = "https://www.semrush.com/analytics/organic/pages/?sortField=&sortDirection=desc&db=us&searchType=domain&q={}"
    _INSTRUCTION = [
        "1. Open your web browser and navigate to the Semrush URL below.",
        "2. Navigate to: {}",
        "3. Follow the on-screen instructions to export the data.",
        "4. Save the exported data to: {}",
    ]

    @property
    def export_name(self):
        return self._EXPORT_NAME

    @property
    def url_template(self):
        return self._URL_TEMPLATE

    @property
    def instruction(self):
        return self._INSTRUCTION

    def _prepare(self):
        project_url = self.project.website.root_url

        formatted_url = self.url_template.format(project_url)

        formatted_instructions = [
            "1. Open your web browser and navigate to the Semrush URL below.",
            f"2. Navigate to: {formatted_url}",
            "3. Follow the on-screen instructions to export the data.",
            f"4. Save the exported data to: {self.temp_path}",
        ]

        print("\n".join(formatted_instructions))

    def _execute(self):
        pass

    def _finalize(self):
        # Any finalization steps, if needed
        print("Finalizing the data post-manual export...")
