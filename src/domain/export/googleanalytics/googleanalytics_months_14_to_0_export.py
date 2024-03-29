import logging

from domain.export.googleanalytics.base_googleanalytics_export import BaseGoogleAnalyticsExport

logger = logging.getLogger(__name__)


class GoogleAnalyticsMonths14To0Export(BaseGoogleAnalyticsExport):

    _EXPORT_NAME = "googleanalytics_months_14_to_0_export"
    _MEASUREMENT_UNIT = "months"
    _BEGIN = 14  # period begins _BEGIN _MEASUREMENT_UNIT ago
    _END = 0  # period ends _END _MEASUREMENT_UNIT ago

    @property
    def export_name(self) -> str:
        return self._EXPORT_NAME

    @property
    def time_unit(self) -> str:
        return self._MEASUREMENT_UNIT

    @property
    def start_date(self) -> int:
        return self._base_date - self._get_relativedelta(self.time_unit, self._BEGIN)

    @property
    def end_date(self) -> int:
        return self._base_date - self._get_relativedelta(self._MEASUREMENT_UNIT, self._END)
