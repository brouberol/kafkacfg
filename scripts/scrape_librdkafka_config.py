import argparse
import contextlib
import json
import re
import subprocess
import tempfile
from collections import defaultdict
from pathlib import Path


def clone_librdkafka_repository(clone_directory: Path):
    if not (clone_directory.exists() and (clone_directory / ".git").exists()):
        subprocess.run(
            [
                "git",
                "clone",
                "https://github.com/confluentinc/librdkafka.git",
                clone_directory,
            ]
        )


def list_librdkafka_tags():
    output = subprocess.run(["git", "tag"], capture_output=True, encoding="utf-8")
    tags = output.stdout.split()
    return [
        tag
        for tag in tags
        if re.match(r"\d\.", tag) or re.match(r"v\d\.\d.\d$", tag)
        if tag != "0.7.0"  # 0.7.0 has no CONFIGURATION.md file
    ]


def checkout_configuration_file_as_of_tag(tag: str):
    subprocess.run(["git", "checkout", tag, "--", "CONFIGURATION.md"])


def parse_configuration_file() -> dict:
    configuration = defaultdict(lambda: defaultdict(dict))
    c_p_value_to_scopes = {
        "C": ("consumer",),
        "P": ("producer",),
        "*": ("consumer", "producer"),
    }
    with open("CONFIGURATION.md") as conf_fd:
        for line in conf_fd:
            if line.startswith("## "):
                scope = line.split()[1].lower()
            elif not line.strip():
                continue
            elif line.startswith(("---", "//", "#")):
                continue
            elif line.startswith("Property"):
                headers = [header.strip().lower() for header in line.split("|")]
            else:
                values = [value.strip() for value in line.split("|")]
                property_data = dict(zip(headers, values))
                property_name = property_data.pop("property")
                if "<br>*Type:" in property_data["description"]:
                    property_description = property_data.pop("description")
                    property_description, property_type = property_description.split(
                        "<br>*Type:"
                    )
                    property_type = property_type.rstrip("*").strip()
                    property_data["description"] = property_description
                    property_data["type"] = property_type
                if consumer_producer_property := property_data.pop("c/p", None):
                    for scope in c_p_value_to_scopes[consumer_producer_property]:
                        configuration[scope][property_name] = property_data | {
                            "scope": scope
                        }
                else:
                    configuration[scope][property_name] = property_data

    return configuration


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--librdkafka-repo-dir",
        help="The directory in which to clone the librdkafka repository",
        type=Path,
    )
    args = parser.parse_args()
    if args.librdkafka_repo_dir is None:
        args.librdkafka_repo_dir = Path(tempfile.mkdtemp())
    return args


def main():
    args = parse_args()
    clone_librdkafka_repository(clone_directory=args.librdkafka_repo_dir)
    with contextlib.chdir(args.librdkafka_repo_dir):
        for tag in list_librdkafka_tags():
            print(f"Parsing CONFIGURATION.md for librdkafka {tag}")
            checkout_configuration_file_as_of_tag(tag)
            config = parse_configuration_file()
            out_filepath = (
                Path(__file__).parent.parent
                / "kafkacfg"
                / "data"
                / "librdkafka"
                / f"{tag.lstrip("v")}.json"
            )
            with open(out_filepath, "w") as out:
                json.dump(config, out, indent=2)


if __name__ == "__main__":
    main()
