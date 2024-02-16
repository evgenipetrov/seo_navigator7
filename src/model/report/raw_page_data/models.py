import logging
from typing import Any, Dict

from django.db import models

from model.base_model_manager import BaseModelManager
from model.core.project.models import ProjectModel
from model.core.url.models import UrlModel, UrlModelManager

logger = logging.getLogger(__name__)


class RawPageDataModelManager(BaseModelManager):
    @staticmethod
    def push(**kwargs: Dict[str, Any]) -> "RawPageDataModel":
        # required relations
        request_url = kwargs.pop("request_url", None)
        request_url_model = UrlModelManager.push(full_address=request_url)
        kwargs["request_url"] = request_url_model

        response_url = kwargs.pop("response_url", None)
        if request_url != response_url:
            response_url_model = UrlModelManager.push(full_address=response_url)
            kwargs["response_url"] = response_url_model
        else:
            kwargs["response_url"] = request_url_model

        identifying_fields: Dict[str, Any] = {
            "project": kwargs.pop("project"),
            "request_url": kwargs["request_url"],
        }
        raw_page_data, created = RawPageDataModel.objects.update_or_create(defaults=kwargs, **identifying_fields)

        if created:
            logger.info(f"Report row {raw_page_data} created successfully.")
        else:
            logger.info(f"Report row {raw_page_data} updated successfully.")

        return raw_page_data

    @staticmethod
    def get_all() -> models.QuerySet:
        return RawPageDataModel.objects.all()


class RawPageDataModel(models.Model):
    # required relations
    project = models.ForeignKey(ProjectModel, on_delete=models.CASCADE, related_name="project")
    request_url = models.ForeignKey(UrlModel, on_delete=models.CASCADE, related_name="request_url")
    response_url = models.ForeignKey(UrlModel, on_delete=models.CASCADE, related_name="response_url")
    # required fields
    status_code = models.IntegerField()
    # optional fields
    page_content_file = models.CharField(max_length=255, blank=True, null=True)
    # system attributes
    created_at = models.DateTimeField(auto_now_add=True)  # auto
    updated_at = models.DateTimeField(auto_now=True)  # auto
    # model manager
    objects: models.Manager = RawPageDataModelManager()

    def __str__(self) -> str:
        return f"RawPageDataModel: request_url = {self.request_url}"

    class Meta:
        db_table = "report_raw_page_data"

        unique_together = (
            "project",
            "request_url",
        )
