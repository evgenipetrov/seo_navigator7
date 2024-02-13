import logging
from abc import ABC, abstractmethod

from django.db import models

logger = logging.getLogger(__name__)


class BaseModelManager(models.Manager, ABC):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    @abstractmethod
    def push(self):
        pass

    def get_instance_by_id(self, instance_id: int) -> "BaseModel":
        return self.get(id=instance_id)
