import logging
import os
from typing import Any

import pandas as pd
from django.conf import settings
from django.core.management.base import BaseCommand, CommandParser
from django.db import transaction

from model.core.project.models import ProjectModel

# Initialize logging
logger = logging.getLogger(__name__)

# Default path for the CSV file
DEFAULT_SAVE_PATH = os.path.join(settings.SECRETS_DIR, "projects.csv")


class Command(BaseCommand):
    help = "Loads Project objects from a CSV file into the database."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "-f",
            "--file",
            type=str,
            help="Path to the CSV file from which to load projects",
            default=DEFAULT_SAVE_PATH,
        )

    def handle(self, *args: Any, **kwargs: Any) -> None:
        file_path = kwargs.get("file", DEFAULT_SAVE_PATH)
        logger.info(f"Starting to load projects from {file_path}")

        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            logger.error(f"Failed to read CSV file at {file_path}: {e}")
            return

        with transaction.atomic():
            for index, row in df.iterrows():
                arguments = row.to_dict()
                try:
                    ProjectModel.objects.push(**arguments)
                except Exception as e:
                    logger.error(f"Error loading project at row {index}: {e}")
                    continue  # Skip to the next row

        self.stdout.write(self.style.SUCCESS(f"Projects loaded from '{file_path}' into the database."))
