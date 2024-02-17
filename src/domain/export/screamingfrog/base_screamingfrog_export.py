import logging
from typing import Any

from domain.export.base_export import BaseExport
from operators.screamingfrog_operator import ScreamingfrogOperator

logger = logging.getLogger(__name__)


class BaseScreamingfrogExport(BaseExport):
    _IS_MANUAL = False

    def __init__(self, project, **kwargs: Any):
        super().__init__(project, **kwargs)
        self._screamingfrog_operator = ScreamingfrogOperator(self.temp_dir)

    @property
    def is_manual(self) -> bool:
        return self._IS_MANUAL

    def _execute(self) -> None:
        self._screamingfrog_operator.run()

    def _cleanup(self) -> None:
        self._empty_temp_dir()
