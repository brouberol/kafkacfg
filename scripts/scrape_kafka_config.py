"""
Scrape the kafka configuration data from the kafka documentation page.

The configuration will be dumped as a JSON file, 'to be used down the road.

"""
import argparse
import json
from collections import defaultdict
from itertools import takewhile
from pathlib import Path
from typing import Callable

import requests
from bs4 import BeautifulSoup

from kafkacfg.version import KAFKA_VERSIONS, KafkaVersion


class BaseKafkaConfig:
    @classmethod
    def fields_for_version(cls, version):
        return cls.fields.get(version, cls.fields["default"])


class KafkaBrokerConfig(BaseKafkaConfig):
    name = "broker"
    fields = {
        "default": ["type", "default", "valid_values", "importance", "update_mode"],
        "v3": [
            "description",
            "type",
            "default",
            "valid_values",
            "importance",
        ],
        "v2": ["default", "description"],
        "v1": ["default", "description"],
    }


class KafkaTopicConfig(BaseKafkaConfig):
    name = "topic"
    fields = {
        "default": [
            "type",
            "default",
            "valid_values",
            "server_default_property",
            "importance",
        ],
        "v3": [
            "default",
            "server_default_property",
            "description",
        ],
        "v2": [
            "default",
            "server_default_property",
            "description",
        ],
    }


class KafkaProducerConfig(BaseKafkaConfig):
    name = "producer"
    fields = {
        "default": [
            "type",
            "default",
            "valid_values",
            "importance",
        ],
        "v3": [
            "default",
            "description",
        ],
        "v2": [
            "default",
            "description",
        ],
    }


class KafkaConsumerConfig(BaseKafkaConfig):
    name = "consumer"
    fields = {
        "default": [
            "type",
            "default",
            "valid_values",
            "importance",
        ],
        "v3": [
            "default",
            "description",
        ],
        "v2": [
            "default",
            "description",
        ],
    }


KAFKA_DOCUMENTATION_URL = "https://kafka.apache.org/{version}/documentation.html"
KAFKA_SECTIONS = [
    KafkaBrokerConfig,
    KafkaTopicConfig,
    KafkaProducerConfig,
    KafkaConsumerConfig,
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-k",
        "--kafka-version",
        help="The kafka version to parse documentation for",
        required=True,
        choices=list(KAFKA_VERSIONS) + ["all"],
    )
    return parser.parse_args()


def kafka_configuration_page_html(version: KafkaVersion) -> str:
    documentation_url = KAFKA_DOCUMENTATION_URL.format(
        version=version.to_url_fragment()
    )
    response = requests.get(documentation_url)
    response.raise_for_status()
    return response.text


def kafka_configuration_page_to_soup_v2(html: str) -> BeautifulSoup:
    soup = BeautifulSoup(html, features="html.parser")
    script = soup.find("script", id="configuration-template")
    script_soup = BeautifulSoup(script.text, features="html.parser")
    return script_soup


def kafka_configuration_page_to_soup_v1(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, features="html.parser")


def extract_elt(elt: str, table, index: int, post_processor=None) -> str | None:
    elts = table.find_all(elt)
    if len(elts) >= index + 1:
        text = elts[index].text or None
        if text and post_processor:
            text = post_processor(text)
        return text


def parse_kafka_configuration_page_v1(soup: BeautifulSoup) -> dict:
    config = defaultdict(lambda: defaultdict(dict))
    for section, table in zip(
        KAFKA_SECTIONS, soup.find_all("table", class_="data-table")
    ):
        if section.name == "topic":
            continue
        for i, tr in enumerate(table.find_all("tr")):
            if i == 0:
                continue
            config_name = extract_elt("td", tr, 0)
            config[section.name][config_name]["default"] = extract_elt("td", tr, 1)
            config[section.name][config_name]["description"] = extract_elt("td", tr, 2)
            config[section.name][config_name]["scope"] = (
                KafkaTopicConfig.name
                if "per-topic override"
                in (config[section.name][config_name]["description"] or "")
                else section.name
            )
    return config


def parse_kafka_configuration_page_v3(soup: BeautifulSoup) -> dict:
    config = defaultdict(lambda: defaultdict(dict))
    for section, table in zip(
        KAFKA_SECTIONS, soup.find_all("table", class_="data-table")
    ):
        for i, tr in enumerate(table.find_all("tr")):
            if i == 0:
                continue
            config_name = extract_elt("td", tr, 0)
            if config_name:
                config_name = config_name.replace("\u00c2\u00a0", "")
            config[section.name][config_name]["scope"] = section.name
            for field_idx, field in enumerate(section.fields_for_version("v3"), 1):
                config[section.name][config_name][field] = extract_elt(
                    "td", tr, field_idx
                )
    return config


def parse_kafka_configuration_page_v2(soup: BeautifulSoup) -> dict:
    config = defaultdict(lambda: defaultdict(dict))
    for section, table in zip(
        KAFKA_SECTIONS, soup.find_all("table", class_="data-table")
    ):
        for i, tr in enumerate(table.find_all("tr")):
            if i == 0:
                continue
            config_name = extract_elt("td", tr, 0)
            if config_name:
                config_name = config_name.replace("\u00c2\u00a0", "")
            config[section.name][config_name]["scope"] = section.name
            for field_idx, field in enumerate(section.fields_for_version("v2"), 1):
                config[section.name][config_name][field] = extract_elt(
                    "td", tr, field_idx
                )
    return config


def parse_kafka_configuration_page_v4(soup: BeautifulSoup) -> dict:
    config = defaultdict(lambda: defaultdict(dict))
    for section, table in zip(KAFKA_SECTIONS, soup.find_all("table")):
        for i, tr in enumerate(table.find_all("tr")):
            if i == 0:
                continue
            config_name = extract_elt("td", tr, 0)
            if config_name:
                config_name = config_name.replace("\u00c2\u00a0", "")
            config[section.name][config_name]["description"] = extract_elt("td", tr, 1)
            config[section.name][config_name]["scope"] = section.name
            for field_idx, field in enumerate(section.fields_for_version("v4"), 2):
                config[section.name][config_name][field] = extract_elt(
                    "td", tr, field_idx
                )
    return config


def parse_kafka_configuration_page_v5(soup: BeautifulSoup) -> dict:
    def post_processor(s: str) -> str:
        if ": " in s:
            return s.split(": ")[1]
        return s

    config = defaultdict(lambda: defaultdict(dict))
    for section, ul in zip(KAFKA_SECTIONS, soup.find_all("ul", class_="config-list")):
        for li in ul.find_all("li", recursive=False):
            if li.find("b") is None:
                continue

            config_name = li.find("b").text.strip()
            description_elts = list(
                takewhile(lambda elt: elt.name != "ul", li.contents[1:])
            )
            description = " ".join([elt.text for elt in description_elts])
            description = description.lstrip(":").strip()
            config[section.name][config_name]["description"] = description
            config_table = li.find("ul")
            if not config_table:
                continue

            config[section.name][config_name]["scope"] = section.name
            for field_idx, field in enumerate(section.fields_for_version("v5")):
                config[section.name][config_name][field] = extract_elt(
                    "li", config_table, field_idx, post_processor
                )

    return config


def parse_kafka_configuration_page_v6(soup: BeautifulSoup) -> dict:
    config = defaultdict(lambda: defaultdict(dict))
    for section, ul in zip(KAFKA_SECTIONS, soup.find_all("ul", class_="config-list")):
        for li in ul.find_all("li"):
            if not li.find("h4"):
                continue
            config_name = li.find("h4").text.strip()
            config[section.name][config_name]["description"] = li.find("p").text.strip()
            config_table = li.find("table")
            config[section.name][config_name]["scope"] = section.name
            for field_idx, field in enumerate(section.fields_for_version("v6")):
                config[section.name][config_name][field] = extract_elt(
                    "td", config_table, field_idx
                )
    return config


def kafka_version_to_soup_extractor(version: KafkaVersion) -> Callable:
    if version >= KafkaVersion(0, 10, 1):
        return kafka_configuration_page_to_soup_v2
    return kafka_configuration_page_to_soup_v1


def kafka_version_to_parser(version: KafkaVersion) -> Callable:
    if version >= KafkaVersion(2, 5, 0):
        return parse_kafka_configuration_page_v6
    if version >= KafkaVersion(2, 4, 0):
        return parse_kafka_configuration_page_v5
    if version >= KafkaVersion(0, 10, 1):
        return parse_kafka_configuration_page_v4
    if version >= KafkaVersion(0, 9, 0):
        return parse_kafka_configuration_page_v3
    if version >= KafkaVersion(0, 8, 1):
        return parse_kafka_configuration_page_v2
    if version >= KafkaVersion(0, 7, 0):
        return parse_kafka_configuration_page_v1


def scrape_kafka_config(version: str):
    version = KafkaVersion.from_str(version)
    html = kafka_configuration_page_html(version)
    soup_extractor = kafka_version_to_soup_extractor(version)
    soup = soup_extractor(html)
    parser = kafka_version_to_parser(version)
    config = parser(soup)
    out_filepath = (
        Path(__file__).parent.parent / "kafkacfg" / "data" / "kafka" / f"{version}.json"
    )
    with open(out_filepath, "w") as out:
        json.dump(config, out, indent=2)


def main():
    args = parse_args()
    if args.kafka_version == "all":
        for version in KAFKA_VERSIONS:
            print(f"Scraping configuration for kafka {version}")
            scrape_kafka_config(version)
    else:
        scrape_kafka_config(args.kafka_version)


if __name__ == "__main__":
    main()
