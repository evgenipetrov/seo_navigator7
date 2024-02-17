from typing import List

from domain.export.googlesearchconsole.base_googlesearchconsole_export import BaseGoogleSearchConsoleExport


class GoogleSearchConsolePageMonths16To0Export(BaseGoogleSearchConsoleExport):
    _EXPORT_NAME = "googlesearchconsole_page_months_0_to_16"
    _MEASUREMENT_UNIT = "months"
    _BEGIN = 14  # period begins _BEGIN _MEASUREMENT_UNIT ago
    _END = 0  # period ends _END _MEASUREMENT_UNIT ago
    _DIMENSIONS: List[str] = ["page"]

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

    @property
    def dimensions(self) -> List[str]:
        return self._DIMENSIONS
