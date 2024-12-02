from collections.abc import MutableMapping
from datetime import UTC, datetime
from typing import Any, cast

import yaml
from mergedeep import merge  # type: ignore
from yaml.loader import SafeLoader

from ..entities import GitReference, MoodlePlugin
from . import config


def add_last_modified_time(
    infrastructure_name: str, yaml: MutableMapping[Any, Any]
) -> MutableMapping[Any, Any]:
    current_time = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
    data = {
        infrastructure_name: {
            "last_modified_at": current_time,
        }
    }
    return merge(yaml, data)


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

    def serialize_testbed_info(
        self,
        infrastructure_name: str,
        new_yaml: MutableMapping[Any, Any],
        should_change_modified_date: bool,
    ) -> None:
        if should_change_modified_date:
            new_yaml = add_last_modified_time(infrastructure_name, new_yaml)
        with open(self.yaml, "w") as f:
            yaml.dump(new_yaml, f)
            f.flush()

    def new_infrastructure(
        self, infrastructure_name: str, plugin: MoodlePlugin, git_ref: GitReference
    ) -> None:
        current_time = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")
        data: dict[str, dict[str, Any]] = {
            infrastructure_name: {
                # created_at and last_modified_at are the same, as the infrastructure is new, so the times must co-incide
                "created_at": current_time,
                "last_modified_at": current_time,
                "plugin": plugin.value,
                "git_ref": {"type": git_ref.type.name, "reference": git_ref.ref},
                "moodles": {},
            }
        }
        # Adding false here to signalize that we do not want to add a "modified_at" field, as we have already done that
        # reason: we want created_at and modified_at to be the same after creating a new infrastructure
        self.merge_into_testbed_info(infrastructure_name, data, False)

    def add_moodles_to_infrastructure(
        self,
        infrastructure_name: str,
        new_moodles: dict[Any, Any],
    ) -> None:
        data = {infrastructure_name: {"moodles": new_moodles}}
        self.merge_into_testbed_info(infrastructure_name, data, True)

    def change_moodle_test_container_status(
        self,
        infrastructure_name: str,
        state: str,
        *versions: str,
    ) -> None:
        data = {
            infrastructure_name: {
                "moodles": {
                    ver: {
                        "status": state,
                    }
                    for ver in versions
                }
            }
        }
        self.merge_into_testbed_info(infrastructure_name, data, True)

    def remove_infrastructure(self, infrastructure_name: str) -> None:
        saved_yaml = self.load_testbed_info()
        saved_yaml.pop(infrastructure_name, None)
        self.delete_testbed_info(infrastructure_name, saved_yaml, False)

    def remove_moodle(self, infrastructure_name: str, version: str) -> None:
        saved_yaml = self.load_testbed_info()
        saved_yaml[infrastructure_name]["moodles"].pop(version)
        self.delete_testbed_info(infrastructure_name, saved_yaml, True)

    def merge_into_testbed_info(
        self,
        infrastructure_name: str,
        data: dict[Any, Any],
        should_change_modified_date: bool = True,
    ) -> None:
        old_yaml = self.load_testbed_info()
        new_yaml = merge(old_yaml, data)
        self.serialize_testbed_info(
            infrastructure_name, new_yaml, should_change_modified_date
        )

    def delete_testbed_info(
        self,
        infrastructure_name: str,
        data: MutableMapping[Any, Any],
        should_change_modified_date: bool = True,
    ) -> None:
        self.serialize_testbed_info(
            infrastructure_name, data, should_change_modified_date
        )

    def infrastructure_info(self, infrastructure_name: str) -> dict[Any, Any]:
        return self.load_testbed_info()[infrastructure_name]

    def get_plugin_for_infrastructure(self, infrastructure_name: str) -> MoodlePlugin:
        return MoodlePlugin(self.infrastructure_info(infrastructure_name)["plugin"])


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
