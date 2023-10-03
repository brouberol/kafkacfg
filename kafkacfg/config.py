import importlib.resources
import json

from .filter import Filter

IGNORED_CONFIGS = (
    "broker.id",
    "broker.rack",
    "brokerid",
    "logs.dir",
    "zookeeper.connect",
)


def load_defaults(kafka_version: str):
    return json.load(
        open(importlib.resources.files("kafkacfg") / f"data/{kafka_version}.json")
    )


def compute_config_overrides(config: dict, defaults: dict) -> list:
    overrides = []
    for config_name, config_value in config.items():
        config_default_value = defaults.get(config_name)
        if (
            config_name not in IGNORED_CONFIGS
            and config_default_value is not None
            and config_value != config_default_value["default"]
        ):
            overrides.append(
                {"name": config_name, "override": config_value} | config_default_value
            )
    return overrides


def explain_config(config: dict, defaults: dict) -> list:
    explained_config = []
    for config_name, config_value in config.items():
        config_default_value = defaults.get(config_name, {})
        explained_config.append(
            {"name": config_name, "override": config_value} | config_default_value
        )
    return explained_config


def filter_config_values(filter_str: str, config: dict, defaults: dict) -> dict:
    matching_configs = {}
    config_filter = Filter.from_str(filter_str)
    for config_name, config_value in defaults.items():
        for predicate in config_filter.predicates:
            full_config_value = config_value | {"name": config_name}
            if not predicate.matches(full_config_value):
                break
        else:
            matching_configs[config_name] = config.get(config_name)

    return explain_config(matching_configs, defaults)
