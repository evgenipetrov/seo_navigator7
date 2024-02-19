import logging
from typing import Any, Dict, List

import pandas as pd
from django.core.exceptions import ValidationError
from django.db import IntegrityError, models

from model.base_model_manager import BaseModelManager
from model.core.project.models import ProjectModel
from model.core.url.models import UrlModel, UrlModelManager

logger = logging.getLogger(__name__)


class UrlInventoryReportModelManager(BaseModelManager):
    @staticmethod
    def push(**kwargs: Dict[str, Any]) -> "UrlInventoryReportModel":
        # Validate 'request_url'
        request_url = kwargs.pop("request_url", None)
        if request_url is None:
            logger.error("No 'request_url' provided to push method")
            return None

        # Attempt to push 'request_url' to 'UrlModel'
        request_url_model = UrlModelManager.push(full_address=request_url)
        if request_url_model is None:
            logger.error(f"Failed to obtain 'UrlModel' for request_url: {request_url}")
            return None
        kwargs["request_url"] = request_url_model

        # Validate 'response_url'
        response_url = kwargs.pop("response_url", None)
        if response_url and response_url != request_url:
            response_url_model = UrlModelManager.push(full_address=response_url)
            if response_url_model is None:
                logger.error(f"Failed to obtain 'UrlModel' for response_url: {response_url}")
                return None
            kwargs["response_url"] = response_url_model
        else:
            kwargs["response_url"] = request_url_model

        # Validate identifying fields
        identifying_fields = {field: kwargs.pop(field) for field in UrlInventoryReportModel.IDENTIFYING_FIELDS if field in kwargs}
        if not identifying_fields:
            logger.error("No identifying fields provided for UrlInventoryReportModel")
            return None

        # Attempt to update or create the UrlInventoryReportModel instance, handling potential exceptions
        try:
            kwargs = {k: v for k, v in kwargs.items() if not pd.isna(v)}
            model_row, created = UrlInventoryReportModel.objects.update_or_create(defaults=kwargs, **identifying_fields)
            if created:
                logger.info(f"[created instance] {model_row}")
            else:
                logger.info(f"[updated instance] {model_row}")
            return model_row
        except IntegrityError as e:
            logger.error(f"Integrity error while pushing UrlInventoryReportModel: {e}")
        except ValidationError as e:
            logger.error(f"Validation error while pushing UrlInventoryReportModel: {e}")
        except Exception as e:
            logger.error(f"Unexpected error while pushing UrlInventoryReportModel: {e}")

        return None

    def get_manual_fields(self) -> List[str]:
        return self.model.IDENTIFYING_FIELDS

    def get_identifying_fields(self) -> List[str]:
        return self.model.MANUAL_FIELDS

    @staticmethod
    def get_all() -> models.QuerySet:
        return UrlInventoryReportModel.objects.all()

    def get_instance_id(self, instance_str: str) -> int:
        try:
            return self.model.objects.get(request_url__full_address=instance_str).id
        except self.model.DoesNotExist:
            logger.error(f"URLInventoryReportModel instance with request_url '{instance_str}' does not exist.")
            return None


class UrlInventoryReportModel(models.Model):
    # List of column names that are updated manually by users. These fields might require
    # special handling during data import/export or synchronization processes.
    MANUAL_FIELDS = [
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
    objects = UrlInventoryReportModelManager()

    def __str__(self) -> str:
        return f"RawPageDataModel: request_url = {self.request_url.full_address}"

    class Meta:
        db_table = "report_raw_page_data"

        unique_together = (
            "project",
            "request_url",
        )
