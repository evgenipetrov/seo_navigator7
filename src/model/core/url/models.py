import logging
from typing import Any, Dict
from urllib.parse import urlparse, urljoin

from django.db import models

from model.base_model_manager import BaseModelManager

logger = logging.getLogger(__name__)


class UrlModelManager(BaseModelManager):
    @staticmethod
    def push(**kwargs: Dict[str, Any]) -> "UrlModel":
        # Separate the identifying fields from the updating fields
        identifying_fields = {"full_address": kwargs.pop("full_address")}
        model_row, created = UrlModel.objects.update_or_create(defaults=kwargs, **identifying_fields)

        if created:
            logger.debug(f"[created instance] {model_row.full_address}")
        else:
            logger.debug(f"[created instance] {model_row.full_address}")

        return model_row

    @staticmethod
    def get_all() -> models.QuerySet:
        return UrlModel.objects.all()

    @staticmethod
    def get_root_url(url: str) -> str:
        parsed_url = urlparse(url)
        root_url_str = f"{parsed_url.scheme}://{parsed_url.netloc}"
        return root_url_str

    @staticmethod
    def get_full_address(root_url: str, path: str) -> str:
        return urljoin(root_url, path)

    @staticmethod
    def is_fragmented(url: str) -> bool:
        return bool(urlparse(url).fragment)


class UrlModel(models.Model):
    # required relations
    # required fields
    full_address = models.URLField(max_length=200, unique=True)  # required
    # optional fields
    # system attributes
    created_at = models.DateTimeField(auto_now_add=True)  # auto
    updated_at = models.DateTimeField(auto_now=True)  # auto
    # model manager
    objects: models.Manager = UrlModelManager()

    def __str__(self) -> str:
        return f"UrlModel: full_address = {self.full_address}"

    class Meta:
        verbose_name = "Url"
        verbose_name_plural = "Urls"

        db_table = "core_urls"
