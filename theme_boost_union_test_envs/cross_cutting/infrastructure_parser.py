from collections.abc import MutableMapping
from typing import Any, cast

import yaml
from mergedeep import merge  # type: ignore
from yaml.loader import SafeLoader

from . import config


class InfrastructureYAMLParser:
    def __init__(self) -> None:
        self.yaml = config().infra_yaml

    def load_testbed_info(self) -> MutableMapping[Any, Any]:
        with open(self.yaml, "r") as f:
            saved_yaml: MutableMapping[Any, Any] = yaml.load(f, Loader=SafeLoader)
            # after initialization, this file will be empty.
            # in this case, we initialize it with an empty dict so that
            # subsequent operations do not fail
            if not saved_yaml:
                saved_yaml = {}
            return saved_yaml

    def serialize_testbed_info(self, new_yaml: MutableMapping[Any, Any]) -> None:
        with open(self.yaml, "w") as f:
            yaml.dump(new_yaml, f)

    def add_infrastructure(self, data: MutableMapping[Any, Any]) -> None:
        saved_yaml = self.load_testbed_info()
        new_yaml = merge(saved_yaml, data)
        self.serialize_testbed_info(new_yaml)

    def remove_infrastructure(self, infrastructure_name: str) -> None:
        saved_yaml = self.load_testbed_info()
        saved_yaml.pop(infrastructure_name, None)
        self.serialize_testbed_info(saved_yaml)

    def remove_moodle(self, infrastructure_name: str, version: str) -> None:
        saved_yaml = self.load_testbed_info()
        saved_yaml[infrastructure_name]["moodles"].pop(version)
        self.serialize_testbed_info(saved_yaml)


def yaml_parser() -> InfrastructureYAMLParser:
    # hacky, but hides implementation detail about the singleton and allows us
    # to avoid the circular dependency issues if each import is directly
    # embedded into the services
    from ..app import Application

    # sometimes mypy is just a funny thing.
    parser = cast(
        InfrastructureYAMLParser,
        Application().cross_cutting_concerns.infrastructure_yaml_parser(),
    )
    return parser
