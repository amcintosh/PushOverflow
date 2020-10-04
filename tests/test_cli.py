import configparser
import datetime
from io import StringIO
import sys
import unittest
from unittest.mock import call, patch

from pushoverflow import cli


class CliTests(unittest.TestCase):

    def test_parser_defaults(self):
        parser = cli.parse_arguments([])
        self.assertEqual(parser.config, "pushoverflow.ini")
        self.assertFalse(parser.log_file)

    def test_parser_args(self):
        parser = cli.parse_arguments(["myfile.ini", "-v"])
        self.assertEqual(parser.config, "myfile.ini")
        self.assertEqual(parser.log_file, ".pushoverflow.log")

        parser = cli.parse_arguments(["-v", "mylog.log", "myfile.ini"])
        self.assertEqual(parser.log_file, "mylog.log")

        parser = cli.parse_arguments(["--verbose", "mylog.log", "myfile.ini"])
        self.assertEqual(parser.config, "myfile.ini")

    def capture_output(self, method):
        temp_stdout = sys.stdout
        try:
            out = StringIO()
            sys.stdout = out
            method()
            output = out.getvalue().strip()
        finally:
            sys.stdout = temp_stdout
        return output

    @patch("pushoverflow.cli.log", autospec=True)
    @patch("pushoverflow.cli.logging", autospec=True)
    @patch("pushoverflow.cli.parse_arguments")
    @patch("pushoverflow.cli.configparser")
    def test_config_file(self, config_parser, arg_parser, logging, log):
        arg_parser().config = "pushoverflow.ini"
        cli.get_configuration()
        self.assertTrue(config_parser.ConfigParser.called)
        config_parser.ConfigParser().read.assert_called_with(
            "pushoverflow.ini")

    @patch("pushoverflow.cli.log", autospec=True)
    @patch("pushoverflow.cli.logging", autospec=True)
    def test_logging_default(self, logging, log):
        cli.get_configuration()

        self.assertEqual(log.setLevel.call_count, 0)
        logging.basicConfig.assert_called_with(format='%(message)s')

    @patch("pushoverflow.cli.log", autospec=True)
    @patch("pushoverflow.cli.logging", autospec=True)
    @patch("pushoverflow.cli.parse_arguments", autospec=True)
    @patch("pushoverflow.cli.configparser")
    def test_logging_verbose(self, config_parser, arg_parser, logging, log):
        arg_parser.return_value.log_file = ".pushoverflow.log"
        logging.DEBUG = 30
        cli.get_configuration()

        log.setLevel.assert_called_with(30)
        logging.basicConfig.assert_called_with(
            filename=arg_parser.return_value.log_file,
            format='%(asctime)s - %(levelname)s: %(message)s')

    @patch("pushoverflow.cli.check_exchange")
    @patch("pushoverflow.cli.get_configuration")
    def test_main_no_config(self, mock_config, check):
        conf = configparser.ConfigParser()
        mock_config.return_value = conf

        output = self.capture_output(cli.main)

        # Missing Global config section
        self.assertTrue(mock_config.called)
        self.assertFalse(check.called)
        self.assertTrue(
            "Missing properties in configuration file: No section:" in output)
        self.assertTrue("'Global'" in output)

        # Missing Pushover config section
        conf.read_dict({
            "Global": {"time_delta_minutes": 60}
            })
        output = self.capture_output(cli.main)
        self.assertTrue(
            "Missing properties in configuration file: No section:" in output)
        self.assertTrue("'Pushover'" in output)

        # Missing Pushover option
        conf.read_dict({
            "Pushover": {"foo": "bar"}
            })
        output = self.capture_output(cli.main)
        self.assertTrue(
            "Missing properties in configuration file: No option" in output)
        self.assertTrue("'appkey'" in output)
        self.assertTrue("'Pushover'" in output)

    @patch("pushoverflow.cli.check_exchange")
    @patch("pushoverflow.cli.get_configuration")
    def test_main_no_exchanges(self, mock_config, check):
        conf = configparser.ConfigParser()
        conf.read_dict({
            "Global": {"time_delta_minutes": 60}
            })
        mock_config.return_value = conf

        cli.main()

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
        cli.main()

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

        cli.main()

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
