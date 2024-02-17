import logging
from typing import Any, Dict, Optional, List

from django.db import models

from model.base_model_manager import BaseModelManager
from model.core.project.models import ProjectModel
from model.core.url.models import UrlModel, UrlModelManager

logger = logging.getLogger(__name__)


class UrlInventoryReportModelManager(BaseModelManager):
    @staticmethod
    def push(**kwargs: Dict[str, Any]) -> "UrlInventoryReportModel":
        # required relations
        request_url: Optional[Dict[str, Any]] = kwargs.pop("request_url")
        request_url_model: "UrlModel" = UrlModelManager.push(full_address=request_url)
        kwargs["request_url"] = request_url_model

        response_url: Optional[Dict[str, Any]] = kwargs.pop("response_url", None)
        if request_url != response_url and response_url is not None:
            response_url_model: "UrlModel" = UrlModelManager.push(full_address=response_url)
            kwargs["response_url"] = response_url_model
        else:
            kwargs["response_url"] = request_url_model

        identifying_fields = {field: kwargs.pop(field) for field in UrlInventoryReportModel.IDENTIFYING_FIELDS if field in kwargs}
        model_row, created = UrlInventoryReportModel.objects.update_or_create(defaults=kwargs, **identifying_fields)

        if created:
            logger.info(f"[created instance] {model_row}")
        else:
            logger.info(f"[updated instance] {model_row}")

        return model_row

    def get_identifying_fields(self) -> List[str]:
        identifying_fields = self.model.IDENTIFYING_FIELDS
        return identifying_fields

    def get_field_names(self) -> List[str]:
        return [field.name for field in UrlInventoryReportModel._meta.fields]

    @staticmethod
    def get_all() -> models.QuerySet:
        return UrlInventoryReportModel.objects.all()


class UrlInventoryReportModel(models.Model):
    # List of column names that are updated manually by users. These fields might require
    # special handling during data import/export or synchronization processes.
    MANUAL_COLUMNS = [
        "note",
    ]
    IDENTIFYING_FIELDS = [
        "project",
        "request_url",
    ]
    # required relations
    project = models.ForeignKey(ProjectModel, on_delete=models.CASCADE, related_name="project")
    request_url = models.ForeignKey(UrlModel, on_delete=models.CASCADE, related_name="request_url")
    response_url = models.ForeignKey(UrlModel, on_delete=models.CASCADE, related_name="response_url")
    # required fields
    status_code = models.IntegerField()
    # optional fields
    page_content_file = models.CharField(max_length=255, blank=True, null=True)
    note = models.CharField(max_length=255, blank=True, null=True)
    # system attributes
    created_at = models.DateTimeField(auto_now_add=True)  # auto
    updated_at = models.DateTimeField(auto_now=True)  # auto
    # model manager
    objects: models.Manager = UrlInventoryReportModelManager()

    def __str__(self) -> str:
        return f"RawPageDataModel: request_url = {self.request_url}"

    class Meta:
        db_table = "report_raw_page_data"

        unique_together = (
            "project",
            "request_url",
        )
