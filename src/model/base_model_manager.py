import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Tuple

from django.db import models

logger = logging.getLogger(__name__)


class BaseModelManager(models.Manager, ABC):
    def __init__(self, *args: Tuple[Any, ...], **kwargs: Dict[str, Any]) -> None:
        super().__init__(*args, **kwargs)

    @abstractmethod
    def push(self) -> models.Model:
        pass

    @staticmethod
    @abstractmethod
    def get_all() -> models.QuerySet:
        pass

    def get_instance_by_id(self, instance_id: int) -> models.Model:
        return self.get(id=instance_id)
