import configparser
import logging
import os

import click

from pushoverflow.core import Notifier

with open(os.path.join(os.path.dirname(__file__), "VERSION")) as f:
    VERSION = f.readlines()[0].strip()

log = logging.getLogger(__name__)


def configure_logging(verbose: bool):
    if verbose:
        logging.basicConfig(format="%(asctime)s - %(levelname)s: %(message)s", level=logging.DEBUG)
    else:
        logging.basicConfig(format="%(message)s", level=logging.INFO)


def get_configuration(config_file: str):
    config = configparser.ConfigParser()
    config.read(config_file)
    return config


def validate_config(config):
    config.get("Global", "check_minutes_back")
    config.get("Pushover", "appkey")
    config.get("Pushover", "userkey")
    config.get("Pushover", "priority")


@click.command()
@click.option('-v', '--verbose', is_flag=True, help="Enable debug logging.")
@click.option('-c', '--config', default="./pushoverflow.ini",
              help="Path to configuration file (Defaults to ./pushoverflow.ini).")
@click.version_option(version=VERSION)
def main(config: str, verbose: bool):
    """Check for new StackExchange questions and notify via Pushover"""
    configure_logging(verbose)
    config = get_configuration(config)

    try:
        validate_config(config)
        notifier = Notifier(config)
        notifier.process()
    except (configparser.NoSectionError, configparser.NoOptionError) as err:
        print("Missing properties in configuration file:", err)
