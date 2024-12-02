import configparser
from unittest.mock import patch

from click.testing import CliRunner

from pushoverflow import cli


@patch("pushoverflow.cli.log", autospec=True)
@patch("pushoverflow.cli.logging", autospec=True)
def test_logging_default(logging, log):
    cli.configure_logging(False)

    assert log.setLevel.call_count == 0
    logging.basicConfig.assert_called_with(format='%(message)s', level=logging.INFO)


@patch("pushoverflow.cli.logging", autospec=True)
def test_logging_verbose(logging):
    cli.configure_logging(True)

    logging.basicConfig.assert_called_with(format='%(asctime)s - %(levelname)s: %(message)s', level=logging.DEBUG)


@patch("pushoverflow.core.check_exchange")
@patch("pushoverflow.cli.get_configuration")
def test_main_no_config(mock_config, mock_check_exchange):
    conf = configparser.ConfigParser()
    mock_config.return_value = conf

    # Missing Global config section
    runner = CliRunner()
    result = runner.invoke(cli.main)
    assert mock_config.called
    assert not mock_check_exchange.called
    assert "Missing properties in configuration file: No section: 'Global'" in result.output

    # Missing Pushover config section
    conf.read_dict({
        "Global": {"check_minutes_back": 60}
    })
    mock_config.return_value = conf
    result = runner.invoke(cli.main)
    assert "Missing properties in configuration file: No section: 'Pushover'" in result.output

    # Missing Pushover option
    conf.read_dict({
        "Pushover": {"foo": "bar"}
    })
    mock_config.return_value = conf
    result = runner.invoke(cli.main)
    assert "Missing properties in configuration file: No option 'appkey' in section: 'Pushover'" in result.output
