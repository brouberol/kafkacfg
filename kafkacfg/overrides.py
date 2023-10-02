IGNORED_CONFIGS = ("broker.id", "brokerid", "zookeeper.connect")


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
