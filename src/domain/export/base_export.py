import logging
import os
import shutil
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any

import pandas as pd
from django.conf import settings

from model.core.project.models import ProjectModel
from operators.dataframe_operator import DataFrameOperator

logger = logging.getLogger(__name__)


class BaseExport(ABC):

    def __init__(self, project: ProjectModel, **kwargs: Any):
        self.project = project
        self.kwargs = kwargs

        self._data = pd.DataFrame()
        self._temp_data = pd.DataFrame()

        # Set up paths for temporary data and final export
        self.temp_dir = os.path.join(project.data_folder, "temp")
        self.save_path = os.path.join(project.data_folder, "exports", self.export_name + ".csv")

        # Ensure temp and export directories exist
        os.makedirs(self.temp_dir, exist_ok=True)
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

    def _empty_temp_dir(self) -> None:
        """Empty the temporary directory."""
        for filename in os.listdir(self.temp_dir):
            file_path = os.path.join(self.temp_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                    logger.info(f"Successfully deleted {file_path}")
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                    logger.info(f"Successfully deleted directory {file_path}")
            except Exception as e:
                logger.error(f"Failed to delete {file_path}. Reason: {e}")

    @abstractmethod
    def _cleanup(self) -> None:
        """perform cleanup."""
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
        if not self._temp_data.empty:
            self._temp_data.to_csv(self.save_path, index=False)
        else:
            print(f"No data to save for '{self.export_name}' export.")

    def _run(self) -> None:
        """Orchestrate the export process by calling the defined methods in order."""
        logger.info("Starting the export process.")
        try:
            self._cleanup()
            logger.info("Cleanup completed.")
            self._prepare()
            logger.info("Preparation completed.")
            self._execute()
            logger.info("Execution completed.")
            if self.is_manual:
                input("Please follow the above instructions to perform the manual export. Press Enter to continue after you're done...")
            if self._temp_data.empty:
                try:
                    self._temp_data = DataFrameOperator.merge_csv(self.temp_dir)
                    logger.info("Merged CSV files from temp directory.")
                except Exception as e:
                    logger.error(f"Failed to load CSV files from temp directory: {e}")
                    return  # or handle the error as appropriate
            self._finalize()
            logger.info("Finalization completed.")
            self._save()
            logger.info("Data saved.")
            self._cleanup()
            logger.info("Final cleanup completed.")
        except Exception as e:
            logger.error(f"An error occurred during the export process: {e}")
        logger.info("Export process completed.")

    @staticmethod
    def _needs_refresh(filepath: str, max_age_days: int = settings.MAX_EXPORT_AGE_DAYS) -> bool:
        last_modified = datetime.fromtimestamp(os.path.getmtime(filepath))
        logger.info(f"Last modified time of the file {filepath}: {last_modified}")
        cutoff = datetime.now() - timedelta(days=max_age_days)
        logger.info(f"Cutoff time: {cutoff}")
        is_refresh_needed = last_modified < cutoff
        if is_refresh_needed:
            logger.info(f"File {filepath} needs to be refreshed.")
        else:
            logger.info(f"File {filepath} does not need to be refreshed.")
        return is_refresh_needed

    def get_data(self) -> pd.DataFrame:
        logger.info(f"Starting to get data for {self.export_name} export.")
        if not self._data.empty:
            logger.info("Data is already loaded.")
            return self._data

        if os.path.exists(self.save_path):
            logger.info(f"Checking if data at {self.save_path} needs to be refreshed.")
            needs_refresh = self._needs_refresh(self.save_path)
            if not needs_refresh:
                logger.info("Data does not need to be refreshed. Loading data from file.")
                try:
                    self._data = pd.read_csv(self.save_path)
                    logger.info("Data loaded successfully.")
                    return self._data
                except Exception as e:
                    logger.error(f"Failed to load data from {self.save_path}: {e}")
            else:
                logger.info("The existing data file is considered old. Refreshing data...")

        try:
            self._run()
            self._data = pd.read_csv(self.save_path)
            logger.info("Data refreshed and loaded successfully.")
            return self._data
        except Exception as e:
            logger.error(f"An error occurred during the data retrieval process: {e}")
