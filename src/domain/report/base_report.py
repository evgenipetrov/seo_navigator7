import logging
import os
from abc import ABC, abstractmethod
from typing import Dict, Type

import pandas as pd
from django.db import models

from domain.export.base_export import BaseExport
from domain.export.export_manager import ExportManager
from model.core.project.models import ProjectModel
from operators.excel_operator import ExcelOperator

logger = logging.getLogger(__name__)


class BaseReport(ABC):
    def __init__(self, project: ProjectModel):
        self.project = project
        self.export_manager = ExportManager(project)

        self._export_data: Dict[str, Type[BaseExport]] = {}
        self._report_base = pd.DataFrame()
        self._report_data = pd.DataFrame()

        self.save_path = os.path.join(project.data_folder, "reports", self.report_name + ".csv")
        self.excel_path = os.path.join("C:\\Users\\evgeni\\OneDrive\\Shared Temp (OneDrive)", "master_data.xlsx")
        # self.excel_path = os.path.join(project.data_folder, "master_data.xlsx")
        self._excel_operator = ExcelOperator(self.excel_path)

        # Ensure temp and export directories exist
        os.makedirs(os.path.dirname(self.save_path), exist_ok=True)

    @property
    @abstractmethod
    def report_name(self) -> str:
        pass

    @property
    @abstractmethod
    def model_class(self) -> models.Model:
        pass

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
    def _finalize(self) -> None:
        """Perform any final processing or cleanup of self.processed_data."""
        # Example: self.processed_data = some_final_processing_function(self.processed_data)

    @abstractmethod
    def _update_db(self) -> None:
        """Save self.processed_data, the final results of the report."""
        # Example: save_to_database(self.processed_data)

    def _dump_report(self) -> None:
        self._report_data.to_csv(self.save_path, index=False)

    def _load_from_db(self) -> pd.DataFrame:
        # Start constructing the base queryset
        queryset = self.model_class.objects.filter(project=self.project)

        # Automatically prefetch all related fields
        for field in self.model_class._meta.get_fields():
            if field.is_relation and field.related_model is not None:
                queryset = queryset.prefetch_related(field.name)

        data_list = []
        for obj in queryset:
            data_dict = {}
            for field in self.model_class._meta.fields:
                field_name = field.name
                value = getattr(obj, field_name)

                # If the field is a ForeignKey, use its string representation
                if field.get_internal_type() == "ForeignKey" and value is not None:
                    value = str(value)

                data_dict[field_name] = value

            # Handle many-to-many fields separately if needed
            for field in self.model_class._meta.many_to_many:
                data_dict[field.name] = ", ".join(str(rel_obj) for rel_obj in getattr(obj, field.name).all())

            data_list.append(data_dict)

        # Convert the list of dictionaries to a DataFrame
        df = pd.DataFrame(data_list)
        return df

    def _save_data(self) -> None:
        # pull manual updates
        # self._excel_operator.pull_updates(self.report_name, self.model_class) #todo: uncomment
        # update db
        self._update_db()
        logger.info(f"[database updated] {self.project.name}")
        self._dump_report()
        logger.info(f"[report saved] {self.save_path}")
        # excel sync
        data = self._load_from_db()
        self._excel_operator.push_updates(self.report_name, data, self.model_class)
        logger.info(f"[master_sheet updated] {self.save_path}")

    def generate(self) -> None:
        self._collect_data()
        self._prepare_data()
        self._process_data()
        self._finalize()
        self._save_data()
