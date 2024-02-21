# import logging
#
# from model.report.new_report.models import NewReportModel  # Replace with your model
#
# from domain.report.base_report import BaseReport
# from model.core.project.models import ProjectModel
#
# logger = logging.getLogger(__name__)
#
#
# class NewReport(BaseReport):
#     _REPORT_NAME = "new_report"  # Replace with your report name
#
#     def __init__(self, project: ProjectModel):
#         super().__init__(project)
#         self.new_data = None  # Replace with your data
#
#     @property
#     def report_name(self) -> str:
#         return self._REPORT_NAME
#
#     @property
#     def model_class(self) -> NewReportModel:  # Replace with your model
#         return NewReportModel
#
#     def _collect_data(self) -> None:
#         # Collect your data here
#         pass
#
#     def _prepare_data(self) -> None:
#         # Prepare your data here
#         pass
#
#     def _process_data(self) -> None:
#         # Process your data here
#         pass
#
#     def _finalize(self) -> None:
#         # Finalize your data here
#         pass
#
#     def _update_db(self) -> None:
#         # Update your database here
#         pass
