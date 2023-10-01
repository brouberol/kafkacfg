"""
Scrape the kafka configuration data from the kafka documentation page.

The configuration will be dumped as a JSON file, 'to be used down the road.

"""
import argparse
import json
from collections import defaultdict
from dataclasses import dataclass
from itertools import takewhile
from pathlib import Path
from typing import Callable

import requests
from bs4 import BeautifulSoup

KAFKA_DOCUMENTATION_URL = "https://kafka.apache.org/{version}/documentation.html"
KAFKA_VERSIONS = (
    "0.7",
    "0.8",
    "0.8.1",
    "0.8.2",
    "0.9.0",
    "0.10.0",
    "0.10.1",
    "0.10.2",
    "0.11.0",
    "1.0",
    "1.1",
    "2.0",
    "2.1",
    "2.2",
    "2.3",
    "2.4",
    "2.5",
    "2.6",
    "2.7",
    "2.8",
    "3.0",
    "3.1",
    "3.2",
    "3.3",
    "3.4",
)


@dataclass
class KafkaVersion:
    major: int
    minor: int
    patch: int
    full_repr: bool = True

    def __ge__(self, other):
        return (self.major, self.minor, self.patch) >= (
            other.major,
            other.minor,
            other.patch,
        )

    @classmethod
    def from_str(cls, version: str):
        if version.count(".") == 2:
            return cls(*map(int, version.split(".")))
        else:
            major, minor = version.split(".")
            return cls(int(major), int(minor), 0, full_repr=False)

    def to_url_fragment(self) -> str:
        if self.full_repr:
            return f"{self.major}{self.minor}{self.patch}"
        return f"{self.major}{self.minor}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-k",
        "--kafka-version",
        help="The kafka version to parse documentation for",
        required=True,
        choices=KAFKA_VERSIONS,
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
    config = defaultdict(dict)
    table = soup.find("table", class_="data-table")
    for i, tr in enumerate(table.find_all("tr")):
        if i == 0:
            continue
        config_name = extract_elt("td", tr, 0)
        config[config_name]["default"] = extract_elt("td", tr, 1)
        config[config_name]["description"] = extract_elt("td", tr, 2)
    return config


def parse_kafka_configuration_page_v2(soup: BeautifulSoup) -> dict:
    config = defaultdict(dict)
    table = soup.find("table", class_="data-table")
    for i, tr in enumerate(table.find_all("tr")):
        if i == 0:
            continue
        config_name = extract_elt("td", tr, 0)
        if config_name:
            config_name = config_name.replace("\u00c2\u00a0", "")
        config[config_name]["description"] = extract_elt("td", tr, 1)
        config[config_name]["type"] = extract_elt("td", tr, 2)
        config[config_name]["default"] = extract_elt("td", tr, 3)
        config[config_name]["valid_values"] = extract_elt("td", tr, 4)
        config[config_name]["importance"] = extract_elt("td", tr, 5)
        config[config_name]["update_mode"] = extract_elt("td", tr, 6)
    return config


def parse_kafka_configuration_page_v3(soup: BeautifulSoup) -> dict:
    config = defaultdict(dict)
    table = soup.find("table")
    for i, tr in enumerate(table.find_all("tr")):
        if i == 0:
            continue
        config_name = extract_elt("td", tr, 0)
        if config_name:
            config_name = config_name.replace("\u00c2\u00a0", "")
        config[config_name]["description"] = extract_elt("td", tr, 1)
        config[config_name]["type"] = extract_elt("td", tr, 2)
        config[config_name]["default"] = extract_elt("td", tr, 3)
        config[config_name]["valid_values"] = extract_elt("td", tr, 4)
        config[config_name]["importance"] = extract_elt("td", tr, 5)
        config[config_name]["update_mode"] = extract_elt("td", tr, 6)
    return config


def parse_kafka_configuration_page_v4(soup: BeautifulSoup) -> dict:
    def post_processor(s: str) -> str:
        if ": " in s:
            return s.split(": ")[1]
        return s

    config = defaultdict(dict)
    ul = soup.find("ul", class_="config-list")
    for li in ul.find_all("li", recursive=False):
        if li.find("b") is None:
            continue

        config_name = li.find("b").text.strip()
        description_elts = list(
            takewhile(lambda elt: elt.name != "ul", li.contents[1:])
        )
        description = " ".join([elt.text for elt in description_elts])
        description = description.lstrip(":").strip()
        config[config_name]["description"] = description
        config_table = li.find("ul")
        if not config_table:
            continue

        config[config_name]["type"] = extract_elt("li", config_table, 0, post_processor)
        config[config_name]["default"] = extract_elt(
            "li", config_table, 1, post_processor
        )
        config[config_name]["valid_values"] = extract_elt(
            "li", config_table, 2, post_processor
        )
        config[config_name]["importance"] = extract_elt(
            "li", config_table, 3, post_processor
        )
        config[config_name]["update_mode"] = extract_elt(
            "li", config_table, 4, post_processor
        )
    return config


def parse_kafka_configuration_page_v5(soup: BeautifulSoup) -> dict:
    config = defaultdict(dict)
    ul = soup.find("ul", class_="config-list")
    for li in ul.find_all("li"):
        if not li.find("h4"):
            continue
        config_name = li.find("h4").text.strip()
        config[config_name]["description"] = li.find("p").text.strip()
        config_table = li.find("table")
        config[config_name]["type"] = extract_elt("td", config_table, 0)
        config[config_name]["default"] = extract_elt("td", config_table, 1)
        config[config_name]["valid_values"] = extract_elt("td", config_table, 2)
        config[config_name]["importance"] = extract_elt("td", config_table, 3)
        config[config_name]["update_mode"] = extract_elt("td", config_table, 4)
    return config


def kafka_version_to_soup_extractor(version: KafkaVersion) -> Callable:
    if version >= KafkaVersion(0, 10, 1):
        return kafka_configuration_page_to_soup_v2
    return kafka_configuration_page_to_soup_v1


def kafka_version_to_parser(version: KafkaVersion) -> Callable:
    if version >= KafkaVersion(2, 5, 0):
        return parse_kafka_configuration_page_v5
    if version >= KafkaVersion(2, 4, 0):
        return parse_kafka_configuration_page_v4
    if version >= KafkaVersion(0, 10, 1):
        return parse_kafka_configuration_page_v3
    if version >= KafkaVersion(0, 9, 0):
        return parse_kafka_configuration_page_v2
    if version >= KafkaVersion(0, 7, 0):
        return parse_kafka_configuration_page_v1


def main():
    args = parse_args()
    version = KafkaVersion.from_str(args.kafka_version)
    html = kafka_configuration_page_html(version)
    soup_extractor = kafka_version_to_soup_extractor(version)
    soup = soup_extractor(html)
    parser = kafka_version_to_parser(version)
    config = parser(soup)
    out_filepath = Path(__file__).parent.parent / "data" / f"{args.kafka_version}.json"
    with open(out_filepath, "w") as out:
        json.dump(config, out, indent=2)


if __name__ == "__main__":
    main()
