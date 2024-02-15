from abc import ABC, abstractmethod

from domain.export.export_runner import ExportManager
from model.core.project.models import ProjectModel


class BaseReport(ABC):
    def __init__(self, project: ProjectModel):
        self.project = project
        self.export_runner = ExportManager()  # Initialize ExportRunner
        self.collected_data = None
        self.prepared_data = None
        self.processed_data = None

    def generate(self):
        self._collect_data()
        self._prepare_data()
        self._process_data()
        self._save_data()

    @abstractmethod
    def _collect_data(self):
        """Execute ExportRunner to collect data, storing results in self.collected_data."""
        # Example: self.collected_data = self.export_runner.run_exports([...])

    @abstractmethod
    def _prepare_data(self):
        """Prepare self.collected_data for processing, storing results in self.prepared_data."""
        # Example: self.prepared_data = some_preparation_function(self.collected_data)

    @abstractmethod
    def _process_data(self):
        """Process self.prepared_data to generate the report's results, storing in self.processed_data."""
        # Example: self.processed_data = some_processing_function(self.prepared_data)

    @abstractmethod
    def _save_data(self):
        """Save self.processed_data, the final results of the report."""
        # Example: save_to_database(self.processed_data)
