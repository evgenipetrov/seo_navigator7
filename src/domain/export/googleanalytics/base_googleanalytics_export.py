import logging
from abc import abstractmethod
from datetime import datetime, timedelta
from typing import Any

from dateutil.relativedelta import relativedelta

from domain.export.base_export import BaseExport
from model.core.project.models import ProjectModel
from model.core.url.models import UrlModelManager
from operators.google_analytics_operator import GoogleAnalyticsOperator

logger = logging.getLogger(__name__)


class BaseGoogleAnalyticsExport(BaseExport):

    _DIMENSIONS = [
        {"name": "pagePath"},
        {"name": "sessionDefaultChannelGrouping"},
    ]
    _METRICS = [
        {"name": "sessions"},
        {"name": "activeUsers"},
        {"name": "averageSessionDuration"},
        {"name": "bounceRate"},
        {"name": "engagedSessions"},
        {"name": "totalRevenue"},
        {"name": "conversions"},
    ]

    def __init__(self, project: ProjectModel, **kwargs: Any) -> None:
        super().__init__(project, **kwargs)
        self.googleanalytics_operator = GoogleAnalyticsOperator()

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
    def period_begin(self) -> str:
        """Flag to indicate if the export requires manual intervention."""
        pass

    @property
    @abstractmethod
    def period_end(self) -> str:
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
        base_date = datetime.today() - timedelta(days=3)  # The earliest point in time we can have complete GA4 data
        self.start_date = base_date - self._get_relativedelta(self.time_unit, self.period_begin)
        self.end_date = base_date - self._get_relativedelta(self.time_unit, self.period_end)

    def _execute(self) -> None:
        self.googleanalytics_operator.set_credentials(self.project.ga4_auth_email)
        self._temp_data = self.googleanalytics_operator.fetch_data(
            ga_property_id=self.project.ga4_property_id,
            start_date=self.start_date,
            end_date=self.end_date,
            dimensions=self._DIMENSIONS,
            metrics=self._METRICS,
        )

    def _finalize(self) -> None:
        self._temp_data["FULL_ADDRESS"] = self._temp_data["pagePath"].apply(lambda page_path: UrlModelManager.get_full_address(self.project.website.root_url.full_address, page_path))
        self._temp_data["IN_GA"] = True
