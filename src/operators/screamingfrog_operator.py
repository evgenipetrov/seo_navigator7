import logging
from typing import List

from django.conf import settings

import docker

logger = logging.getLogger(__name__)


class ScreamingfrogOperator:
    _crawl_config: str

    def __init__(self, temp_dir: str):
        self.temp_dir = temp_dir
        self.parameters = ["--headless", "--overwrite"]
        self.image = f"{settings.SCREAMINGFROG_IMAGE_NAME}:{settings.SCREAMINGFROG_IMAGE_TAG}"
        self.client = docker.from_env()

    def set_crawl_config(self, seospiderconfig: str) -> None:
        self._crawl_config = seospiderconfig
        self.parameters.append(f"--config {seospiderconfig}")

    def set_export_tabs(self, export_tabs: List[str]) -> None:
        export_tabs_str = ",".join(export_tabs)
        self.parameters.append(f'--export-tabs "{export_tabs_str}"')

    def set_crawl_url(self, url: str) -> None:
        self.parameters.append(f"--crawl {url}")

    def set_sitemap_url(self, sitemap_url: str) -> None:
        self.parameters.append(f"--crawl-sitemap {sitemap_url}")

    def set_crawl_list(self, listfile: str) -> None:
        self.parameters.append(f"--crawl-list {listfile}")

    def run(self) -> None:
        # volume_mapping = f"{self.temp_dir}:/export"
        # full_command = f"docker run --rm -v {volume_mapping} -d {self.image} {' '.join(self.parameters)}"
        # logger.info(f"Executing Docker command: {full_command}")

        volumes = {self.temp_dir: {"bind": "/export", "mode": "rw"}}
        parameters = " ".join(self.parameters)
        try:
            container = self.client.containers.run(
                image=self.image,
                command=parameters,
                volumes=volumes,
                detach=True,
                auto_remove=True,
            )
            for line in container.logs(stream=True):
                logger.info(f"{self._crawl_config}: {line.strip().decode()}")
        except Exception as e:
            logger.error(f"An error occurred while running the container: {e}")
