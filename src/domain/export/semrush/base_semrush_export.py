import logging
from abc import abstractmethod
from typing import Any

from domain.export.base_export import BaseExport
from model.core.project.models import ProjectModel

logger = logging.getLogger(__name__)


class BaseSemrushExport(BaseExport):
    _IS_MANUAL = True

    def __init__(self, project: ProjectModel, **kwargs: Any):
        super().__init__(project, **kwargs)
        self.kwargs = kwargs

    @property
    def is_manual(self) -> bool:
        return self._IS_MANUAL

    @property
    @abstractmethod
    def url_template(self) -> str:
        """Flag to indicate if the export requires manual intervention."""
        pass

    @abstractmethod
    def _print_instructions(self) -> None:
        """Flag to indicate if the export requires manual intervention."""
        pass

    def _cleanup(self) -> None:
        self._empty_temp_dir()

    def _execute(self) -> None:
        pass

    def _finalize(self) -> None:
        pass
