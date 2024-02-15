from abc import abstractmethod
from typing import Any, List

from domain.export.base_export import BaseExport
from model.core.project.models import ProjectModel


class BaseSemrushExport(BaseExport):
    _IS_MANUAL = True

    def __init__(self, project: ProjectModel, **kwargs: Any):
        super().__init__(project, **kwargs)
        self.kwargs = kwargs
        self.api_key = kwargs

    @property
    def is_manual(self) -> bool:
        return self._IS_MANUAL

    @property
    @abstractmethod
    def url_template(self) -> str:
        """Flag to indicate if the export requires manual intervention."""
        pass

    @property
    @abstractmethod
    def instruction(self) -> List[str]:
        """Flag to indicate if the export requires manual intervention."""
        pass
