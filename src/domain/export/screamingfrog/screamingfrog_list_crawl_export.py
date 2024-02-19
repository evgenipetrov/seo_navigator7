import logging
import os
import posixpath
from typing import Any, List

from domain.export.screamingfrog.base_screamingfrog_export import BaseScreamingfrogExport

logger = logging.getLogger(__name__)


class ScreamingFrogListCrawlExport(BaseScreamingfrogExport):
    _EXPORT_NAME: str = "screamingfrog_list_crawl_export"
    _CRAWL_CONFIG: str = "/seospiderconfig/listcrawl.seospiderconfig"
    _EXPORT_TABS: List[str] = ["Internal:HTML"]

    def __init__(self, project, **kwargs: Any):
        super().__init__(project, **kwargs)

    @property
    def export_name(self) -> str:
        return self._EXPORT_NAME

    def _set_crawl_config(self) -> None:
        self._screamingfrog_operator.set_crawl_config(self._CRAWL_CONFIG)

    def _set_export_tabs(self) -> None:
        self._screamingfrog_operator.set_export_tabs(self._EXPORT_TABS)

    def _prepare(self) -> None:
        url_list_filename = "crawl_list.txt"
        urls = self.kwargs.get("urls", [])
        local_crawl_list_file_path = os.path.join(self.temp_dir, url_list_filename)
        with open(local_crawl_list_file_path, "w") as file:
            for url in urls:
                file.write(f"{url}\n")
        docker_crawl_list_file_path = posixpath.join("/export", url_list_filename)
        self._screamingfrog_operator.set_crawl_list(docker_crawl_list_file_path)

    def _finalize(self) -> None:
        pass
