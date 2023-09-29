from pathlib import Path

import requests

from ..cross_cutting import config, log


class MoodleCache:
    def __init__(self, cache_dir: str, download_url: str) -> None:
        # yaml doesn't allow string concatenation, so we are doing this here
        # make sure moodle cache folder is in app core pwd
        self.cache_dir = config().working_dir / Path(cache_dir)
        if not self.cache_dir.exists():
            self.cache_dir.mkdir(parents=True)
        self.url = download_url

    def get(self, version: str) -> Path:
        moodle_tar_name = _generate_file_name(version)
        archive_path: Path = self.cache_dir / moodle_tar_name
        # if the selected moodle version isn't on disk, we need to download it
        if not archive_path.exists():
            self.__download(moodle_tar_name, archive_path)
        # else, just return the path to the source of the selected moodle
        # version, as we have the file on disk; effectively hitting our 'cache'
        else:
            log().info(f"getting moodle {version} from cache")
        return archive_path

    def __download(self, file_name: str, destination: Path) -> None:
        dl_link_for_vers = self.url + file_name
        log().info(f"downloading from {dl_link_for_vers}")
        resp = requests.get(dl_link_for_vers, allow_redirects=True)
        with destination.open(mode="wb") as file:
            file.write(resp.content)
        log().info(f"download done, saved to cache: {destination}")


_DEFAULT_ARCHIVE_EXT = ".tar.gz"


def _generate_file_name(version: str) -> str:
    if not version.startswith("v"):
        version = f"v{version}"
    return f"{version}{_DEFAULT_ARCHIVE_EXT}"
