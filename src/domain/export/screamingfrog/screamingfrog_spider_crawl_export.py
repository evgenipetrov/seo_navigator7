import logging
from typing import List

from domain.export.screamingfrog.base_screamingfrog_export import BaseScreamingfrogExport

logger = logging.getLogger(__name__)


class ScreamingFrogSpiderCrawlExport(BaseScreamingfrogExport):
    _EXPORT_NAME: str = "screamingfrog_spider_crawl_export"
    _CRAWL_CONFIG: str = "/seospiderconfig/spidercrawl.seospiderconfig"
    _EXPORT_TABS: List[str] = ["Internal:HTML"]

    def __init__(self, project):
        super().__init__(project)

    @property
    def export_name(self) -> str:
        return self._EXPORT_NAME

    def _set_crawl_config(self) -> None:
        self._screamingfrog_operator.set_crawl_config(self._CRAWL_CONFIG)

    def _set_export_tabs(self) -> None:
        self._screamingfrog_operator.set_export_tabs(self._EXPORT_TABS)

    def _prepare(self) -> None:
        self._screamingfrog_operator.set_crawl_url(self.project.website.root_url.full_address)

    def _finalize(self) -> None:
        self._temp_data["IN_CRAWL"] = True
