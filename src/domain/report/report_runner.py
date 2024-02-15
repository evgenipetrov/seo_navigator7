from domain.report.url_inventory_report import UrlInventoryReport
from model.core.project.models import ProjectModel

# Register your report classes in a dictionary
report_classes = {
    "url_inventory": UrlInventoryReport,
}


class ReportRunner:
    @staticmethod
    def run(project: ProjectModel) -> None:
        for report_name, report_class in report_classes.items():
            print(f"Running {report_name} report for project {project.name}")
            report = report_class(project)
            report.generate()
