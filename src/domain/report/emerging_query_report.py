import logging

import pandas as pd

from domain.report.base_report import BaseReport
from model.core.project.models import ProjectModel
from model.report.emerging_query_report.models import EmergingQueryReportModel
from operators.dataframe_operator import DataFrameOperator

logger = logging.getLogger(__name__)


class EmergingTopicsReport(BaseReport):
    _REPORT_NAME = "emerging_topics"  # Replace with your report name

    def __init__(self, project: ProjectModel):
        super().__init__(project)

    @property
    def report_name(self) -> str:
        return self._REPORT_NAME

    @property
    def model_class(self) -> EmergingQueryReportModel:  # Replace with your model
        return EmergingQueryReportModel

    def _collect_data(self) -> None:
        self._export_data["googleasearchconsole_query_page_months_16_to_1_export"] = self.export_manager.get_data("googleasearchconsole_query_page_months_16_to_1_export")
        self._export_data["googleasearchconsole_query_page_months_1_to_0_export"] = self.export_manager.get_data("googleasearchconsole_query_page_months_1_to_0_export")
        self._export_data["googleasearchconsole_query_page_weeks_78_to_1_export"] = self.export_manager.get_data("googleasearchconsole_query_page_weeks_78_to_1_export")
        self._export_data["googleasearchconsole_query_page_weeks_1_to_0_export"] = self.export_manager.get_data("googleasearchconsole_query_page_weeks_1_to_0_export")

    def _prepare_data(self) -> None:
        new_topics_month = self._export_data["googleasearchconsole_query_page_months_1_to_0_export"][
            ~self._export_data["googleasearchconsole_query_page_months_1_to_0_export"]["query"].isin(self._export_data["googleasearchconsole_query_page_months_16_to_1_export"]["query"])
        ]
        new_topics_week = self._export_data["googleasearchconsole_query_page_weeks_1_to_0_export"][
            ~self._export_data["googleasearchconsole_query_page_weeks_1_to_0_export"]["query"].isin(self._export_data["googleasearchconsole_query_page_weeks_78_to_1_export"]["query"])
        ]
        topics = []
        topics.extend(new_topics_month["query"].tolist())
        topics.extend(new_topics_week["query"].tolist())

        # prepare for final list crawl
        unique_topics = list(set(topics))

        model_fields = self.model_class.objects.get_field_names()  # Use your method to get field names
        model_fields.append("BASE_TOPIC")  # Add BASE_URL to the list of columns
        self._report_base = pd.DataFrame(columns=model_fields)
        self._report_base["BASE_TOPIC"] = pd.Series(unique_topics)

    def _process_data(self) -> None:
        self._export_data["googleasearchconsole_query_page_months_1_to_0_export"]["last_month"] = True
        column_mapper = {
            "topic": "query",
            "url_last_month": "page",
            "impressions_last_month": "impressions",
            "clicks_last_month": "clicks",
            "ctr_last_month": "ctr",
            "position_last_month": "position",
            "from_last_month": "last_month",
        }
        self._report_base = DataFrameOperator.update_df_from_df(self._report_base, self._export_data["googleasearchconsole_query_page_months_1_to_0_export"], "BASE_TOPIC", "query", column_mapper)
        self._export_data["googleasearchconsole_query_page_weeks_1_to_0_export"]["last_week"] = True
        column_mapper = {
            "url_last_week": "page",
            "impressions_last_week": "impressions",
            "clicks_last_week": "clicks",
            "ctr_last_week": "ctr",
            "position_last_week": "position",
            "from_last_week": "last_week",
        }
        self._report_base = DataFrameOperator.update_df_from_df(self._report_base, self._export_data["googleasearchconsole_query_page_weeks_1_to_0_export"], "BASE_TOPIC", "query", column_mapper)
        self._report_data = self._report_base

    def _finalize(self) -> None:
        self._report_data["project"] = self.project
        # Drop all columns that start with "BASE_"
        base_columns = [col for col in self._report_data.columns if col.startswith("BASE_")]
        self._report_data.drop(columns=base_columns, inplace=True)

    def _update_db(self) -> None:
        for index, row in self._report_data.iterrows():
            arguments = row.to_dict()
            self.model_class.objects.push(**arguments)
        logger.info(f"[database updated] {self.project.name}")
