from pathlib import Path

import requests
from loguru import logger

from ..utils.config import get_config

DEFAULT_ARCHIVE_EXT = ".tar.gz"


class MoodleCache:
    def __init__(self, cache_dir: str, download_url: str) -> None:
        # yaml doesn't allow string concatenation, so we are doing this here
        # make sure moodle cache folder is in app core pwd
        self.cache_dir = get_config().working_dir / Path(cache_dir)
        if not self.cache_dir.exists():
            self.cache_dir.mkdir(parents=True)
        self.url = download_url

    def get(self, version: str) -> Path:
        source_archive = self.cache_dir / create_file_name(version)
        if not source_archive.exists():
            self.__download(version, source_archive)
            logger.info("done downloading")
        else:
            logger.info(f"getting moodle {version} from cache")
        # else, just return the path to the source of the selected moodle
        # version, as we have the file on disk; effectively hitting our 'cache'
        return source_archive

    def __download(self, version: str, dl_path: Path) -> None:
        dl_link_for_vers = self.url + create_file_name(version)
        logger.info(f"downloading moodle {version} from {dl_link_for_vers} into cache")
        resp = requests.get(dl_link_for_vers, allow_redirects=True)
        total = int(resp.headers.get("content-length", 0))
        print(total)
        with dl_path.open(mode="wb") as file:
            logger.info(f"streaming {create_file_name(version)} to file")
            file.write(resp.content)


def create_file_name(version: str) -> str:
    if not version.startswith("v"):
        version = f"v{version}"
    return f"{version}{DEFAULT_ARCHIVE_EXT}"
