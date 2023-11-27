import os
import shutil
from pathlib import Path

from ..cross_cutting import config, log, template_engine
from . import GitReference, GitReferenceType, GitRepository, clone_moodle_docker_repo


class Testbed:
    def __init__(self) -> None:
        self.working_dir = config().working_dir
        self.nginx_dir = config().nginx_dir
        self.infra_yaml = config().infra_yaml
        self.moodle_cache_dir = config().moodle_cache_dir
        self.docker_repo_dir = config().moodle_docker_dir

    def init(self) -> None:
        # ugly sentinel value, but works good enough
        initialized = True
        if not self.working_dir.exists():
            log().info(f"creating test bed @ {self.working_dir}")
            self.working_dir.mkdir()
            initialized = False
        if not self.moodle_cache_dir.exists():
            log().info(f"creating moodle cache directory @ {self.moodle_cache_dir}")
            self.moodle_cache_dir.mkdir()
            initialized = False
        if not self.nginx_dir.exists():
            log().info(f"creating nginx config directory @ {self.nginx_dir}")
            self.nginx_dir.mkdir()
            initialized = False
        if not self.docker_repo_dir.exists():
            log().info(f"cloning moodle_docker repo into {self.docker_repo_dir}")
            moodle_docker = clone_moodle_docker_repo()
            # copy template files into the cloned moodle docker repo to ensure
            # every newly created environment has access to those without hassle
            for file in template_engine().template_files:
                if file.name.endswith("html.j2"):
                    continue
                if file.name == "nginx.conf":
                    continue
                shutil.copy(file, moodle_docker.repo.working_dir)
            initialized = False
        if not self.infra_yaml.exists():
            log().info(
                f"creating infrastructure serialization file: {self.infra_yaml.name}"
            )
            self.infra_yaml.touch()
            initialized = False
        if initialized:
            log().info(
                f"no further action needed, test bed has already been initialized: {self.working_dir}"
            )
        else:
            log().info(f"test bed is now initialized: {self.working_dir}")
