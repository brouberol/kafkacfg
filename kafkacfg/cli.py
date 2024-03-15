import json
from pathlib import Path

import click

from .broker import BrokerAttributes
from .config import (
    compute_config_overrides,
    difference_between_versions,
    explain_config,
    filter_config_values,
    load_defaults,
    recommend_config,
)
from .exceptions import InvalidPredicateAttribute
from .parser import parse_properties_config
from .version import KAFKA_VERSIONS, LIBRDKAFKA_VERSIONS, __version__


def validate_source_and_version(ctx, _, value):
    """Validate the tuple of (source, version) values"""
    if "source" not in ctx.params:
        return value

    source = ctx.params["source"]
    version = value
    if source == "librdkafka" and version not in LIBRDKAFKA_VERSIONS:
        raise click.BadParameter(
            f"{version} is not a valid librdkafka version. Choose from {', '.join(LIBRDKAFKA_VERSIONS)}"
        )
    elif source == "kafka" and version not in KAFKA_VERSIONS:
        raise click.BadParameter(
            f"{version} is not a valid kafka version. Choose from {', '.join(KAFKA_VERSIONS)}"
        )
    return value


def validate_config_type_and_source(ctx, _, value):
    """Validate the tuple of (source, config_type) values"""
    source = ctx.params["source"]
    config_type = value
    if source == "librdkafka" and config_type in ("broker", "topic"):
        raise click.BadParameter(
            f"Invalid librdkafka config type '{config_type}'. Choose from 'consumer' or 'producer'"
        )
    return value


def config_type_default():
    ctx = click.get_current_context()
    source = ctx.params["source"]
    if source == "librdkafka":
        return "producer"
    else:
        return "broker"


version_choice = click.option(
    "-v",
    "--version",
    help="The version of the software associated to the configuration source (kafka, librdkafka) you are running",
    callback=validate_source_and_version,
    required=True,
)

config_type_choice = click.option(
    "-c",
    "--config-type",
    type=click.Choice(("broker", "consumer", "producer", "topic")),
    help="The type of configuration to evaluate",
    callback=validate_config_type_and_source,
    default=lambda: config_type_default(),
    show_default=True,
)

source_choice = click.option(
    "-s",
    "--source",
    type=click.Choice(("kafka", "librdkafka")),
    help="The source of configuration to evaluate: the kafka or librdkafka documentation",
    default="kafka",
    # useful to always have ctx.params['source'] in validate_source_version,
    # whatever the order with which --source and --version were passed in
    is_eager=True,
    show_default=True,
)


@click.group()
@click.version_option(__version__)
def kafkacfg():
    """A kafka configuration inspector"""


@kafkacfg.command()
@source_choice
@version_choice
@config_type_choice
@click.argument("config_file", type=click.Path(exists=True))
def overrides(
    source: str,
    version: str,
    config_file: click.Path,
    config_type: str,
):
    """Display the config overrides from a kafka configuration file"""
    config = parse_properties_config(Path(config_file))
    defaults = load_defaults(version, source=source)[config_type]
    config_overrides = compute_config_overrides(config, defaults)
    click.echo(json.dumps(config_overrides))


@kafkacfg.command()
@source_choice
@version_choice
@config_type_choice
@click.argument("config_file", type=click.Path(exists=True))
def explain(
    source: str,
    version: str,
    config_file: click.Path,
    config_type: str,
):
    """Display information about each config tunable from a kafka configuration file"""
    config = parse_properties_config(Path(config_file))
    defaults = load_defaults(version, source=source)[config_type]
    config_overrides = explain_config(config, defaults)
    click.echo(json.dumps(config_overrides))


@kafkacfg.command()
@source_choice
@version_choice
@click.option("-c", "--config-file", type=click.Path(exists=True))
@click.argument("query", type=str)
def query(source: str, version: str, query: str, config_file: click.Path):
    """Query kafka configuration tunables by their attributes

    Examples:

    \b
    # Query a kafka config details by tunable name
    $ kafkacfg query -v 1.1 'name=replica.fetch.min.bytes'
    \b
    # Query multiple kafka config details by tunable name
    $ kafkacfg query -v 1.1 'name=replica.fetch.min.bytes,socket.request.max.bytes'

    \b
    # Query multiple kafka config details by tunable name pattern
    $ kafkacfg query -v 1.1 'name=socket.*.buffer.bytes'

    \b
    # Query a kafka config details by importance
    $ kafkacfg query -v 1.1 'importance=high'

    \b
    # Query multiple kafka config details by importance and name pattern
    $ kafkacfg query -v 1.1 'importance=high;name=*.bytes'

    \b
    # Query kafka confifg details and compare results with config overrides
    $ kafkacfg query -v 1.1 -c server.properties 'importance=high;name=*.bytes'

    \b
    # Query librdkafka confifg details and compare results with config overrides
    $ kafkacfg query --source librdkafka -v 2.0.0  'importance=high;name=*.bytes'

    """
    config = parse_properties_config(Path(config_file)) if config_file else {}
    defaults = load_defaults(version, source=source)
    try:
        filtered_configs = filter_config_values(query, config, defaults)
    except InvalidPredicateAttribute as exc:
        click.echo(exc, err=True)
    else:
        click.echo(json.dumps(filtered_configs))


@kafkacfg.command()
@version_choice
@click.option(
    "--broker-num-cpus",
    type=int,
    help="The number of processors per broker",
    required=True,
)
@click.option(
    "--broker-num-disks",
    type=int,
    help="The number of hard drives per broker",
    required=True,
)
@click.argument("config_file", type=click.Path(exists=True))
def recommends(
    version: str,
    config_file: click.Path,
    broker_num_cpus: int,
    broker_num_disks: int,
):
    """Emit sourced configuration recommendations based on broker attributes"""
    config = parse_properties_config(Path(config_file))
    defaults = load_defaults(version, source="kafka")
    broker_attrs = BrokerAttributes(
        num_cpus=broker_num_cpus, num_disks=broker_num_disks
    )
    recos = recommend_config(config, defaults, broker_attrs)
    for i, reco in enumerate(recos, 1):
        click.echo(f"Recommendation {i}: set {reco}")


@kafkacfg.command()
@source_choice
@click.option(
    "-f",
    "--from-version",
    callback=validate_source_and_version,
    help="The initial version",
)
@click.option(
    "-t",
    "--to-version",
    callback=validate_source_and_version,
    help="The destination version",
)
@config_type_choice
def diff(source: str, from_version: str, to_version: str, config_type: str):
    """Display the changes in configuration between 2 kafka versions"""
    click.echo(
        json.dumps(
            difference_between_versions(
                from_version, to_version, config_type, source=source
            )
        )
    )
