import importlib.resources
import json
from pathlib import Path

import click

from .overrides import compute_config_overrides
from .parser import parse_properties_config
from .version import KAFKA_VERSIONS


@click.group()
def kafkacfg():
    ...


@kafkacfg.command()
@click.option(
    "-c",
    "--config-file",
)
@click.option("-k", "--kafka-version", type=click.Choice(KAFKA_VERSIONS))
def overrides(config_file: str, kafka_version: str):
    """Compute the overrides and associated config description from a kafka configuration file."""
    config = parse_properties_config(Path(config_file))
    defaults = json.load(
        open(importlib.resources.files("kafkacfg") / f"data/{kafka_version}.json")
    )
    config_overrides = compute_config_overrides(config, defaults)
    print(json.dumps(config_overrides))
