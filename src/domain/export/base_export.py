import os
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any

import pandas as pd
from django.conf import settings

from model.core.project.models import ProjectModel
from operators.dataframe_operator import DataFrameOperator


class BaseExport(ABC):

    def __init__(self, project: ProjectModel, **kwargs: Any):
        self.project = project
        self.kwargs = kwargs

        self._data = pd.DataFrame()
        self._temp_data = pd.DataFrame()

        # Set up paths for temporary data and final export
        self.temp_path = os.path.join(project.data_folder, "temp")
        self.save_path = os.path.join(project.data_folder, "exports", self.export_name + ".csv")

        # Ensure temp and export directories exist
        os.makedirs(self.temp_path, exist_ok=True)
        os.makedirs(os.path.dirname(self.save_path), exist_ok=True)

    @property
    @abstractmethod
    def export_name(self) -> str:
        """A unique name for the export type."""
        pass

    @property
    @abstractmethod
    def is_manual(self) -> bool:
        """Flag to indicate if the export requires manual intervention."""
        pass

    @abstractmethod
    def _prepare(self) -> None:
        """Prepare the environment or settings for the export."""
        pass

    @abstractmethod
    def _execute(self) -> None:
        """Execute the main export routine, possibly populating self._temp_data."""
        pass

    @abstractmethod
    def _finalize(self) -> None:
        """Finalize and possibly transform self._temp_data post-export."""
        pass

    def _save(self) -> None:
        """Save the finalized data to a CSV file in the export directory."""
        if self._temp_data is not None:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(self.save_path), exist_ok=True)
            # Save the DataFrame to CSV
            self._temp_data.to_csv(self.save_path, index=False)
        else:
            print(f"No data to save for '{self.export_name}' export.")

    def _run(self) -> None:
        """Orchestrate the export process by calling the defined methods in order."""
        self._prepare()
        self._execute()
        if self.is_manual:
            input("Please follow the above instructions to perform the manual export. Press Enter to continue after you're done...")
        if self._temp_data is None:
            try:
                self._temp_data = DataFrameOperator.merge_csv(self.temp_path)
            except Exception as e:
                print(f"Failed to load CSV files from temp directory: {e}")
                return  # or handle the error as appropriate
        self._finalize()
        self._save()

    @staticmethod
    def _needs_refresh(filepath: str, max_age_days: int = settings.MAX_EXPORT_AGE_DAYS) -> bool:
        last_modified = datetime.fromtimestamp(os.path.getmtime(filepath))
        cutoff = datetime.now() - timedelta(days=max_age_days)
        return last_modified < cutoff

    def get_data(self) -> pd.DataFrame:
        if not self._data.empty:
            return self._data

        if os.path.exists(self.save_path):
            needs_refresh = self._needs_refresh(self.save_path)
            if not needs_refresh:
                self._data = pd.read_csv(self.save_path)
                return self._data
            else:
                print("The existing data file is considered old. Refreshing data...")

        self._run()
        self._data = pd.read_csv(self.save_path)
        return self._data
