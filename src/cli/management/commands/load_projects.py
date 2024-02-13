import logging
import os

import pandas as pd
from django.conf import settings
from django.core.management.base import BaseCommand

from models.core.project.models import ProjectModelManager

# Initialize logging
logger = logging.getLogger(__name__)

# Default path for the CSV file
DEFAULT_SAVE_PATH = os.path.join(settings.SECRETS_DIR, "projects.csv")


class Command(BaseCommand):
    help = "Loads Project objects from a CSV file into the database."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "-f",
            "--file",
            type=str,
            help="Path to the CSV file from which to load projects",
            default=DEFAULT_SAVE_PATH,
        )

    def handle(self, *args, **kwargs) -> None:
        file_path = kwargs.get("file", DEFAULT_SAVE_PATH)
        logger.info(f"Starting to load projects from {file_path}")

        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            logger.error(f"Failed to read CSV file at {file_path}: {e}")
            return

        for index, row in df.iterrows():
            arguments = row.to_dict()
            logger.info(f"Creating project with arguments: {arguments}")
            project = ProjectModelManager.push(**arguments)

        self.stdout.write(self.style.SUCCESS(f"Projects loaded from '{file_path}' into the database."))
