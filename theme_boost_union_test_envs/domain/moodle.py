import time
from http import HTTPStatus
from pathlib import Path
from typing import cast

import requests
from requests.exceptions import HTTPError

from ..cross_cutting import config, log
from ..exceptions import InvalidMoodleVersionError


class MoodleDownloader:
    def __init__(self, url: str, retries: int, retry_timeout: int) -> None:
        self.url = url
        self.retries = retries
        self.retry_codes = [
            HTTPStatus.TOO_MANY_REQUESTS,
            HTTPStatus.INTERNAL_SERVER_ERROR,
            HTTPStatus.BAD_GATEWAY,
            HTTPStatus.SERVICE_UNAVAILABLE,
            HTTPStatus.GATEWAY_TIMEOUT,
        ]
        self.retry_timeout = retry_timeout

    def download(self, file_name: str, destination: Path) -> None:
        for retry in range(self.retries):
            try:
                dl_link_for_vers = self.url + file_name
                log().info(
                    f"downloading from {dl_link_for_vers} - try {retry+1} from {self.retries}"
                )
                resp = requests.get(dl_link_for_vers, allow_redirects=True)
                resp.raise_for_status()
                with destination.open(mode="wb") as file:
                    file.write(resp.content)
                log().info(f"download done, saved to cache: {destination}")
                # if successful, we need to break out of the loop
                break
            except HTTPError as e:
                if e.response.status_code in self.retry_codes:
                    # retry after exponential backoff
                    time.sleep(retry * self.retry_timeout)
                    continue
                raise e


class MoodleCache:
    def __init__(self, downloader: MoodleDownloader) -> None:
        self.directory = config().moodle_cache_dir
        self.downloader = downloader

    def get(self, version: str) -> Path:
        moodle_tar_name = _generate_archive_file_name(version)
        archive_path = self.directory / moodle_tar_name
        # if the selected moodle version isn't on disk, we need to download it
        if not archive_path.exists():
            log().info(f"cache miss - trying to download moodle {version}")
            try:
                self.downloader.download(moodle_tar_name, archive_path)
            except HTTPError as e:
                if e.response.status_code == HTTPStatus.NOT_FOUND:
                    raise InvalidMoodleVersionError(version)
        # else, just return the path to the source of the selected moodle
        # version, as we have the file on disk; effectively hitting our 'cache'
        else:
            log().info(f"cache hit - getting moodle {version} from disk")
        return archive_path


_DEFAULT_ARCHIVE_EXT = ".tar.gz"


def _generate_archive_file_name(version: str) -> str:
    if not version.startswith("v"):
        version = f"v{version}"
    return f"{version}{_DEFAULT_ARCHIVE_EXT}"


def moodle_cache() -> MoodleCache:
    # hacky, but hides implementation detail about the singleton and allows us
    # to avoid the circular dependency issues if each import is directly
    # embedded into the services
    from ..app import Application

    # sometimes mypy is just a funny thing.
    return cast(MoodleCache, Application().domain.moodle_cache())
