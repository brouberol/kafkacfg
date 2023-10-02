import importlib.resources
import json
from pathlib import Path

import click

from .config import compute_config_overrides, explain_config
from .parser import parse_properties_config
from .version import KAFKA_VERSIONS

kafka_version_choice = click.option(
    "-k",
    "--kafka-version",
    type=click.Choice(KAFKA_VERSIONS),
    help="The kafka version you are running",
    required=True,
)


@click.group()
def kafkacfg():
    """A kafka configuration inspector"""


@kafkacfg.command()
@kafka_version_choice
@click.argument("config_file")
def overrides(kafka_version: str, config_file: str):
    """Display the config overrides from a kafka configuration file"""
    config = parse_properties_config(Path(config_file))
    defaults = json.load(
        open(importlib.resources.files("kafkacfg") / f"data/{kafka_version}.json")
    )
    config_overrides = compute_config_overrides(config, defaults)
    click.echo(json.dumps(config_overrides))


@kafkacfg.command()
@kafka_version_choice
@click.argument("config_file")
def explain(kafka_version: str, config_file: str):
    """Display information about each config tunable from a kafka configuration file"""
    config = parse_properties_config(Path(config_file))
    defaults = json.load(
        open(importlib.resources.files("kafkacfg") / f"data/{kafka_version}.json")
    )
    config_overrides = explain_config(config, defaults)
    click.echo(json.dumps(config_overrides))
