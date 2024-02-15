from domain.export.semrush.semrush_analytics_organic_pages_domain import SemrushAnalyticsOrganicPagesDomainExport


class ExportManager:
    def __init__(self):
        # Mapping of export type identifiers to export classes
        self.available_exports = {
            "semrush_analytics_organic_pages_domain": SemrushAnalyticsOrganicPagesDomainExport,
            # Add more exports as needed
        }

    def get_data(self, export_type, project, **kwargs):
        # Check if the requested export type is available
        if export_type in self.available_exports:
            # Instantiate the export class with the project and any additional kwargs
            export_instance = self.available_exports[export_type](project, **kwargs)
            # Run the export
            return export_instance.get_data()
        else:
            raise ValueError(f"Export type '{export_type}' is not available.")
