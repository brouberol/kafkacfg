IGNORED_CONFIGS = ("broker.id", "brokerid", "zookeeper.connect")


def compute_config_overrides(config: dict, defaults: dict) -> dict:
    overrides = {}
    for config_name, config_value in config.items():
        config_default_value = defaults.get(config_name)
        if (
            config_name not in IGNORED_CONFIGS
            and config_value != config_default_value["default"]
        ):
            overrides[config_name] = config_default_value | {"override": config_value}
    return overrides
