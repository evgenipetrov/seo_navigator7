import logging
import os
from abc import ABC, abstractmethod
from typing import Dict

import pandas as pd
from django.db import models

from domain.export.export_manager import ExportManager
from model.core.project.models import ProjectModel
from operators.excel_operator import ExcelOperator

logger = logging.getLogger(__name__)


class BaseReport(ABC):
    def __init__(self, project: ProjectModel):
        self.project = project
        self.export_manager = ExportManager(project)

        self._export_data: Dict[str, pd.DataFrame] = {}
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

    @abstractmethod
    def _prepare_data(self) -> None:
        """Prepare self.collected_data for processing, storing results in self.prepared_data."""

    @abstractmethod
    def _process_data(self) -> None:
        """Process self.prepared_data to generate the report's results, storing in self.processed_data."""

    @abstractmethod
    def _finalize(self) -> None:
        """Perform any final processing or cleanup of self.processed_data."""

    @abstractmethod
    def _update_db(self) -> None:
        """Save self.processed_data, the final results of the report."""

    def _dump_report(self) -> None:
        self._report_data.to_csv(self.save_path, index=False)
        logger.info(f"[report saved] {self.save_path}")

    def _load_flat_from_db(self) -> pd.DataFrame:
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

    def _push_updates_to_excel(self) -> None:
        data = self._load_flat_from_db()
        self._excel_operator.push_updates(self.report_name, data, self.model_class)
        logger.info(f"[master_sheet updated] {self.save_path}")

    def _pull_updates_from_excel(self) -> None:
        excel_data = self._excel_operator.pull_updates(self.report_name, self.model_class)
        fk_fields = self.model_class.objects.get_foreign_key_fields()

        for index, row in excel_data.iterrows():
            query_kwargs: Dict[str, str] = {}
            update_fields: Dict[str, str] = {}

            for field, value in row.items():
                if field in fk_fields:
                    related_model = fk_fields[field]
                    related_model_manager = related_model.objects
                    fk_id = related_model_manager.get_instance(str(value))
                    if fk_id is not None:
                        query_kwargs[f"{field}_id"] = fk_id
                    else:
                        logger.warning(f"Could not find related instance for field '{field}' with value '{value}'")
                        break
                elif field in self.model_class.objects.get_manual_fields() and value:  # Check for non-empty manual field
                    update_fields[field] = value

            else:  # This else clause runs if no break occurs in the loop
                if update_fields:  # Proceed only if there are non-empty manual fields to update
                    db_entry = self.model_class.objects.filter(**query_kwargs).first()
                    if db_entry:
                        for field, value in update_fields.items():
                            setattr(db_entry, field, value)
                        db_entry.save()
                        logger.info(f"Updated database entry for {query_kwargs}")
                    else:
                        logger.info(f"No entry found matching {query_kwargs}, consider creating a new instance")

    def _save_data(self) -> None:
        # get manually updated column values from the Excel file
        self._pull_updates_from_excel()
        # update db
        self._update_db()
        # save the report to a CSV file
        self._dump_report()
        # push updates to the Excel file
        self._push_updates_to_excel()

    def generate(self) -> None:
        self._collect_data()
        self._prepare_data()
        self._process_data()
        self._finalize()
        self._save_data()
