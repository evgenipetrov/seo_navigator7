from typing import Any

import pandas as pd

from domain.export.semrush.semrush_analytics_organic_pages_domain import SemrushAnalyticsOrganicPagesDomainExport
from model.core.project.models import ProjectModel


class ExportManager:

    AVAILABLE_EXPORTS = {
        "semrush_analytics_organic_pages_domain": SemrushAnalyticsOrganicPagesDomainExport,
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
