import unittest
from unittest.mock import patch
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
    @patch("pushoverflow.cli.parse_arguments")
    def test_logging_verbose(self, args, logging, log):
        args().log_file = ".pushoverflow.log"
        logging.DEBUG = 30
        cli.get_configuration()

        log.setLevel.assert_called_with(30)
        logging.basicConfig.assert_called_with(
            filename=args().log_file,
            format='%(asctime)s - %(levelname)s: %(message)s')
