import importlib.resources
import json
from pathlib import Path

import click

from .overrides import compute_config_overrides
from .parser import parse_properties_config
from .version import KAFKA_VERSIONS


@click.group()
def kafkacfg():
    """A kafka configuration inspector"""


@kafkacfg.command()
@click.option(
    "-k",
    "--kafka-version",
    type=click.Choice(KAFKA_VERSIONS),
    help="The kafka version you are running",
)
@click.argument("config_file")
def overrides(kafka_version: str, config_file: str):
    """Display the config overrides from a kafka configuration file"""
    config = parse_properties_config(Path(config_file))
    defaults = json.load(
        open(importlib.resources.files("kafkacfg") / f"data/{kafka_version}.json")
    )
    config_overrides = compute_config_overrides(config, defaults)
    click.echo(json.dumps(config_overrides))
