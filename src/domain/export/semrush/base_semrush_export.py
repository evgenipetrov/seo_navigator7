from abc import abstractmethod

from domain.export.base_export import BaseExport


class BaseSemrushExport(BaseExport):
    _IS_MANUAL = True

    def __init__(self, project, **kwargs):
        super().__init__(project, **kwargs)
        self.kwargs = kwargs
        self.api_key = kwargs

    @property
    def is_manual(self):
        return self._IS_MANUAL

    @property
    @abstractmethod
    def url_template(self):
        """Flag to indicate if the export requires manual intervention."""
        pass

    @property
    @abstractmethod
    def instruction(self):
        """Flag to indicate if the export requires manual intervention."""
        pass
