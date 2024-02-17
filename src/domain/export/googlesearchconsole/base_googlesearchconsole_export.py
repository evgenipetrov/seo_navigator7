import logging
from abc import abstractmethod
from datetime import datetime, timedelta
from typing import Any

from dateutil.relativedelta import relativedelta

from domain.export.base_export import BaseExport
from model.core.project.models import ProjectModel
from model.core.url.models import UrlModelManager
from operators.google_search_console_operator import GoogleSearchConsoleOperator

logger = logging.getLogger(__name__)


class BaseGoogleSearchConsoleExport(BaseExport):
    def __init__(self, project: ProjectModel, **kwargs: Any) -> None:
        super().__init__(project, **kwargs)
        self._googlesearchconsole_operator = GoogleSearchConsoleOperator()
        self._base_date = datetime.today() - timedelta(days=3)  # The earliest point in time we can have complete GSC data

    @property
    def is_manual(self) -> bool:
        return False

    @property
    @abstractmethod
    def time_unit(self) -> str:
        """Flag to indicate if the export requires manual intervention."""
        pass

    @property
    @abstractmethod
    def start_date(self) -> str:
        """Flag to indicate if the export requires manual intervention."""
        pass

    @property
    @abstractmethod
    def end_date(self) -> str:
        """Flag to indicate if the export requires manual intervention."""
        pass

    @property
    @abstractmethod
    def dimensions(self) -> str:
        """Flag to indicate if the export requires manual intervention."""
        pass

    def _cleanup(self) -> None:
        pass

    @staticmethod
    def _get_relativedelta(measurement_unit: str, value: int) -> relativedelta:
        if measurement_unit == "months":
            return relativedelta(months=value)
        elif measurement_unit == "weeks":
            return relativedelta(weeks=value)
        # Add more cases as needed
        raise ValueError(f"Unsupported measurement unit: {measurement_unit}")

    def _prepare(self) -> None:
        pass

    def _execute(self) -> None:
        self._googlesearchconsole_operator.set_credentials(self.project.gsc_auth_email)
        self._temp_data = self._googlesearchconsole_operator.fetch_data(
            site_url=self.project.gsc_property_name,
            start_date=self.start_date,
            end_date=self.end_date,
            dimensions=self.dimensions,
        )

    def _finalize(self) -> None:
        self._temp_data = self._temp_data[~self._temp_data["page"].apply(UrlModelManager.is_fragmented)]
        self._temp_data["IN_GSC"] = True
