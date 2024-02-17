import logging
from typing import List

from domain.export.screamingfrog.base_screamingfrog_export import BaseScreamingfrogExport

logger = logging.getLogger(__name__)


class ScreamingFrogSitemapCrawlExport(BaseScreamingfrogExport):
    _EXPORT_NAME: str = "screamingfrog_sitemap_crawl_export"
    _CRAWL_CONFIG: str = "/seospiderconfig/sitemapcrawl.seospiderconfig"
    _EXPORT_TABS: List[str] = ["Internal:HTML"]

    def __init__(self, project):
        super().__init__(project)

    @property
    def export_name(self) -> str:
        return self._EXPORT_NAME

    def _prepare(self) -> None:
        self._screamingfrog_operator.set_sitemap_url(self.project.website.sitemap_url.full_address)
        self._screamingfrog_operator.set_crawl_config(self._CRAWL_CONFIG)
        self._screamingfrog_operator.set_export_tabs(self._EXPORT_TABS)

    def _finalize(self) -> None:
        self._temp_data["IN_SITEMAP"] = True
