import configparser
import datetime
import unittest
from unittest.mock import call, patch
from click.testing import CliRunner
from pushoverflow import cli


class CliTests(unittest.TestCase):

    @patch("pushoverflow.cli.log", autospec=True)
    @patch("pushoverflow.cli.logging", autospec=True)
    def test_logging_default(self, logging, log):
        cli.configure_logging(False)

        self.assertEqual(log.setLevel.call_count, 0)
        logging.basicConfig.assert_called_with(format='%(message)s', level=logging.INFO)

    @patch("pushoverflow.cli.log", autospec=True)
    @patch("pushoverflow.cli.logging", autospec=True)
    def test_logging_verbose(self, logging, log):
        cli.configure_logging(True)

        logging.basicConfig.assert_called_with(format='%(asctime)s - %(levelname)s: %(message)s', level=logging.DEBUG)

    @patch("pushoverflow.cli.check_exchange")
    @patch("pushoverflow.cli.get_configuration")
    def test_main_no_config(self, mock_config, check):
        conf = configparser.ConfigParser()
        mock_config.return_value = conf

        runner = CliRunner()
        result = runner.invoke(cli.main)
        # Missing Global config section
        self.assertTrue(mock_config.called)
        self.assertFalse(check.called)
        self.assertTrue("Missing properties in configuration file: No section:" in result.output)
        self.assertTrue("'Global'" in result.output)

        # Missing Pushover config section
        conf.read_dict({
            "Global": {"time_delta_minutes": 60}
        })
        result = runner.invoke(cli.main)
        self.assertTrue("Missing properties in configuration file: No section:" in result.output)
        self.assertTrue("'Pushover'" in result.output)

        # Missing Pushover option
        conf.read_dict({
            "Pushover": {"foo": "bar"}
        })
        result = runner.invoke(cli.main)
        self.assertTrue("Missing properties in configuration file: No option" in result.output)
        self.assertTrue("'appkey'" in result.output)
        self.assertTrue("'Pushover'" in result.output)

    @patch("pushoverflow.cli.check_exchange")
    @patch("pushoverflow.cli.get_configuration")
    def test_main_no_exchanges(self, mock_config, check):
        conf = configparser.ConfigParser()
        conf.read_dict({
            "Global": {"time_delta_minutes": 60}
        })
        mock_config.return_value = conf

        runner = CliRunner()
        runner.invoke(cli.main)

        self.assertTrue(mock_config.called)
        self.assertFalse(check.called)

    @patch("pushoverflow.cli.send_questions_to_pushover")
    @patch("pushoverflow.cli.check_exchange")
    @patch("pushoverflow.cli.get_check_time")
    @patch("pushoverflow.cli.get_configuration")
    def test_main_with_exchanges(self, mock_config, now, check, pushover):
        now.return_value = datetime.datetime.now()
        conf = configparser.ConfigParser()
        conf.read_dict({
            "Global": {"time_delta_minutes": 60},
            "Pushover": {"appkey": "some_key", "userkey": "some_key"},
            "stackoverflow": {"tags": "python"}
        })
        mock_config.return_value = conf

        runner = CliRunner()
        runner.invoke(cli.main)

        self.assertTrue(mock_config.called)
        check.assert_called_once_with(conf["stackoverflow"], now())
        self.assertFalse(pushover.called)

    @patch("pushoverflow.cli.send_questions_to_pushover")
    @patch("pushoverflow.cli.check_exchange")
    @patch("pushoverflow.cli.get_check_time")
    @patch("pushoverflow.cli.get_configuration")
    def test_main_with_exchange_questions(self, mock_config, now, check,
                                          pushover):
        now.return_value = datetime.datetime.now()
        conf = configparser.ConfigParser()
        conf.read_dict({
            "Global": {"time_delta_minutes": 60},
            "Pushover": {"appkey": "some_key", "userkey": "some_key"},
            "stackoverflow": {"tags": "python"},
            "scifi": {"tags": "star-trek"}
        })
        mock_config.return_value = conf
        check.return_value = ["test"]

        runner = CliRunner()
        runner.invoke(cli.main)

        self.assertTrue(mock_config.called)
        check.assert_has_calls([
            call(conf["stackoverflow"], now()),
            call(conf["scifi"], now())
        ], any_order=True)

        self.assertTrue(pushover.called)
        pushover.assert_has_calls([
            call(conf["Pushover"], "stackoverflow", ["test"]),
            call(conf["Pushover"], "scifi", ["test"])
        ], any_order=True)
