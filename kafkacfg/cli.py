import json
from pathlib import Path

import click

from .config import (
    compute_config_overrides,
    explain_config,
    filter_config_values,
    load_defaults,
)
from .exceptions import InvalidPredicateAttribute
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
    defaults = load_defaults(kafka_version)
    config_overrides = compute_config_overrides(config, defaults)
    click.echo(json.dumps(config_overrides))


@kafkacfg.command()
@kafka_version_choice
@click.argument("config_file")
def explain(kafka_version: str, config_file: str):
    """Display information about each config tunable from a kafka configuration file"""
    config = parse_properties_config(Path(config_file))
    defaults = load_defaults(kafka_version)
    config_overrides = explain_config(config, defaults)
    click.echo(json.dumps(config_overrides))


@kafkacfg.command()
@kafka_version_choice
@click.option(
    "-q",
    "--query",
    help="A query used to select kafka tunables by their attributes",
    required=True,
)
@click.argument("config_file")
def filter(kafka_version: str, query: str, config_file: str):
    """Query kafka configuration tunables via their attribute

    Examples:

    \b
    # Fetch a config details by tunable name
    $ kafkacfg filter --query name=replica.fetch.min.bytes -k 1.1 server.properties

    \b
    # Fetch multiple config details by tunable name
    $ kafkacfg filter --query name=replica.fetch.min.bytes,socket.request.max.bytes -k 1.1 server.properties

    \b
    # Fetch multiple config details by tunable name pattern
    $ kafkacfg filter --query name=socket.*.buffer.bytes -k 1.1 server.properties

    \b
    # Fetch a config details by importance
    $ kafkacfg filter --query importance=high -k 1.1 server.properties

    \b
    # Fetch multiple config details by importance and name pattern
    $ kafkacfg filter --query importance=high;name=*.bytes -k 1.1 server.properties

    """
    config = parse_properties_config(Path(config_file))
    defaults = load_defaults(kafka_version)
    try:
        filtered_configs = filter_config_values(query, config, defaults)
    except InvalidPredicateAttribute as exc:
        click.echo(exc, err=True)
    else:
        click.echo(json.dumps(filtered_configs))
