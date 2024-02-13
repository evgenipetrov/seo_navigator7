import logging
from urllib.parse import urlparse

from django.db import models

from models.base_model_manager import BaseModelManager

logger = logging.getLogger(__name__)


class UrlModelManager(BaseModelManager):
    @staticmethod
    def push(**kwargs) -> "UrlModel":
        # Separate the identifying fields from the updating fields
        identifying_fields = {"full_address": kwargs.pop("full_address")}
        url, created = UrlModel.objects.update_or_create(defaults=kwargs, **identifying_fields)

        if created:
            logger.info(f"Url {url.full_address} created successfully.")
        else:
            logger.info(f"Url {url.full_address} updated successfully.")

        return url

    @staticmethod
    def get_root_url(url: str) -> str:
        parsed_url = urlparse(url)
        root_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        return root_url


class UrlModel(models.Model):
    # fields
    full_address = models.URLField(max_length=200, unique=True)

    # system attributes
    created_at = models.DateTimeField(auto_now_add=True)  # auto
    updated_at = models.DateTimeField(auto_now=True)  # auto

    # managers
    objects = UrlModelManager()

    def __str__(self):
        return self.full_address

    class Meta:
        verbose_name = "Url"
        verbose_name_plural = "Urls"

        db_table = "core_urls"
