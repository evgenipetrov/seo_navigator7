import logging
from abc import ABC, abstractmethod

import pandas as pd

from domain.export.export_manager import ExportManager
from model.core.project.models import ProjectModel

logger = logging.getLogger(__name__)


class BaseReport(ABC):
    def __init__(self, project: ProjectModel):
        self.project = project
        self.export_manager = ExportManager(project)
        self._export_data = {}
        self._report_base = pd.DataFrame()
        self._report_data = pd.DataFrame()

    def generate(self) -> None:
        self._collect_data()
        self._prepare_data()
        self._process_data()
        self._save_data()

    @abstractmethod
    def _collect_data(self) -> None:
        """Execute ExportRunner to collect data, storing results in self.collected_data."""
        # Example: self.collected_data = self.export_runner.run_exports([...])

    @abstractmethod
    def _prepare_data(self) -> None:
        """Prepare self.collected_data for processing, storing results in self.prepared_data."""
        # Example: self.prepared_data = some_preparation_function(self.collected_data)

    @abstractmethod
    def _process_data(self) -> None:
        """Process self.prepared_data to generate the report's results, storing in self.processed_data."""
        # Example: self.processed_data = some_processing_function(self.prepared_data)

    @abstractmethod
    def _save_data(self) -> None:
        """Save self.processed_data, the final results of the report."""
        # Example: save_to_database(self.processed_data)
