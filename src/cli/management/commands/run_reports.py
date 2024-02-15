import logging
from typing import Any

from django.core.management.base import BaseCommand, CommandParser

from domain.report.report_runner import ReportRunner
from model.core.project.models import ProjectModelManager

# Initialize logging
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Loads Project objects from a CSV file into the database."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "-p",
            "--project-name",
            type=str,
            help="Project to run reports for.",
        )

    def handle(self, *args: Any, **kwargs: Any) -> None:
        project_name = kwargs.get("project")
        if project_name:
            logger.info(f"Starting to run reports for project {project_name}")
        else:
            project_model_manager: ProjectModelManager = ProjectModelManager()
            projects = project_model_manager.get_all()
            for project in projects:
                logger.info(f"Starting to run reports for project {project.name}")
                # Run reports for project
                ReportRunner.run(project)
        self.stdout.write(self.style.SUCCESS("Reports run complete."))
