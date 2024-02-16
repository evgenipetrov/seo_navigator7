import logging
import os
from typing import Any

import pandas as pd
from django.conf import settings
from django.core.management.base import BaseCommand, CommandParser

from model.core.project.models import ProjectModelManager
from model.core.url.models import UrlModelManager
from model.core.website.models import WebsiteModelManager

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

        for index, row in df.iterrows():
            arguments = row.to_dict()
            base_url = arguments.pop("base_url")
            root_url = UrlModelManager.get_root_url(base_url)
            root_url_model = UrlModelManager.push(full_address=root_url)
            sitemap_url_model = UrlModelManager.push(full_address=arguments.pop("sitemap_url"))
            kwargs = {
                "root_url": root_url_model,
                "sitemap_url": sitemap_url_model,
            }
            website_model = WebsiteModelManager.push(**kwargs)
            arguments["website"] = website_model
            ProjectModelManager.push(**arguments)

        self.stdout.write(self.style.SUCCESS(f"Projects loaded from '{file_path}' into the database."))
