import configparser
from pathlib import Path


def parse_properties_config(filepath: Path) -> dict:
    """Parse a .properties file and return its content as a dict

    Note: a properties file is just an ini file without a global section heading.

    """
    config_text = f"[{configparser.DEFAULTSECT}]\n" + filepath.read_text()
    config = configparser.ConfigParser()
    config.read_string(config_text)
    return dict(config[configparser.DEFAULTSECT])
