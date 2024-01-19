import importlib.resources
import json
from collections import ChainMap

from .broker import BrokerAttributes
from .filter import Filter
from .recommendation import recommendations

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
    """Augment each non-default configuration tunable with its associated metadata"""
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
    """Augment each configuration tunable with its associated metadata"""
    explained_config = []
    for config_name, config_value in config.items():
        config_default_value = defaults.get(config_name, {})
        explained_config.append(
            {"name": config_name, "override": config_value} | config_default_value
        )
    return explained_config


def filter_config_values(filter_str: str, config: dict, defaults: dict) -> list:
    output = []
    config_filter = Filter.from_str(filter_str)
    for section_defaults in defaults.values():
        matching_configs = {}
        for config_name, config_value in section_defaults.items():
            for predicate in config_filter.predicates:
                full_config_value = config_value | {"name": config_name}
                if not predicate.matches(full_config_value):
                    break
            else:
                matching_configs[config_name] = config.get(config_name)

        if matching_configs:
            output.extend(explain_config(matching_configs, section_defaults))
    return output


def recommend_config(
    config: dict, defaults: dict, broker_attrs: BrokerAttributes
) -> list[str]:
    """Inspect the broker configuration and recommend some configuration tweaks"""
    recos = []
    defaults_kv = {
        cfg_name: cfg_data["default"]
        for cfg_name, cfg_data in defaults["broker"].items()
    }
    broker_config = ChainMap(config, defaults_kv)
    for recommendation in recommendations:
        config_current_value = broker_config.get(recommendation.config)
        config_recommended_value_rendered_formula = recommendation.formula.format(
            **vars(broker_attrs)
        )
        config_recommended_value = eval(config_recommended_value_rendered_formula)
        if not recommendation.operator(
            int(config_current_value), config_recommended_value
        ):
            recos.append(recommendation.render(vars(broker_attrs)))
    return recos


def difference_between_versions(
    from_version: str, to_version: str, config_type: str
) -> list:
    """Compute the configuration delta between two versions.

    This will highlight the configuration tunables:
    - that have been introduced
    - that have been deprecated
    - which default value has changed

    """
    diff = []
    old_defaults = load_defaults(kafka_version=from_version)
    new_defaults = load_defaults(kafka_version=to_version)
    new_flags = set(new_defaults[config_type]) - set(old_defaults[config_type])
    removed_flags = set(old_defaults[config_type]) - set(new_defaults[config_type])
    old_default_col = f"default ({from_version})"
    new_default_col = f"default ({to_version})"

    # Deprecated configs
    for config_name, config_meta in old_defaults[config_type].items():
        if config_name not in removed_flags:
            continue
        config_meta[old_default_col] = config_meta.pop("default")
        config_meta[new_default_col] = "[REMOVED]"
        config_meta = {
            "name": config_name,
            "status": "deprecated",
        } | config_meta  # name 1st means that it will be in the first table column
        diff.append(config_meta)

    # New configs
    for config_name, config_meta in new_defaults[config_type].items():
        if config_name not in new_flags:
            continue
        config_meta[old_default_col] = "[ABSENT]"
        config_meta[new_default_col] = config_meta.pop("default")
        config_meta = {
            "name": config_name,
            "status": "new",
        } | config_meta  # name 1st means that it will be in the first table column
        diff.append(config_meta)

    # Configs with new defaults
    for config_name, config_meta in new_defaults[config_type].items():
        if old_config_meta := old_defaults.get(config_name):
            old_default = old_config_meta["default"]
            new_default = config_meta["default"]
            if old_default != new_default:
                # sometimes old_default = 1234 and new_default = 1234 (xxx)
                if (
                    isinstance(new_default, str)
                    and isinstance(old_default, str)
                    and old_default in new_default
                ):
                    continue
                config_meta[old_default_col] = old_default
                config_meta[new_default_col] = config_meta.pop("default")
                config_meta = (
                    {
                        "name": config_name,
                        "status": "changed",
                    }
                    | config_meta
                )  # name 1st means that it will be in the first table column
                diff.append(config_meta)

    return diff
