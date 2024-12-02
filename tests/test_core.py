import configparser
import datetime
import unittest
from unittest.mock import call, patch

from pushoverflow.core import Notifier


class CoreTests(unittest.TestCase):

    @patch("pushoverflow.core.check_exchange")
    def test_main_no_exchanges(self, mock_handle):
        conf = configparser.ConfigParser()
        conf.read_dict({
            "Global": {"check_minutes_back": 60}
        })

        notifier = Notifier(conf)
        notifier.process()

        self.assertFalse(mock_handle.called)

    @patch.object(Notifier, "handle_questions")
    @patch("pushoverflow.core.check_exchange")
    @patch.object(Notifier, "get_check_time")
    def test_main_with_exchange(self, mock_check_time, mock_check_exchange, mock_handle):
        mock_check_time.return_value = datetime.datetime.now()
        conf = configparser.ConfigParser()
        conf.read_dict({
            "Global": {"check_minutes_back": 60},
            "Pushover": {"appkey": "some_key", "userkey": "some_key"},
            "stackoverflow": {"tags": "python"}
        })

        notifier = Notifier(conf)
        notifier.process()

        mock_check_exchange.assert_called_once_with(conf["stackoverflow"], mock_check_time())
        self.assertFalse(mock_handle.called)

    @patch.object(Notifier, "handle_questions")
    @patch("pushoverflow.core.check_exchange")
    @patch.object(Notifier, "get_check_time")
    def test_main_with_exchanges(self, mock_check_time, mock_check_exchange, mock_handle):
        mock_check_time.return_value = datetime.datetime.now()
        conf = configparser.ConfigParser()
        conf.read_dict({
            "Global": {"check_minutes_back": 60},
            "Pushover": {"appkey": "some_key", "userkey": "some_key"},
            "stackoverflow": {"tags": "python"},
            "scifi": {"tags": "star-trek"}
        })
        mock_check_exchange.return_value = ["test"]

        notifier = Notifier(conf)
        notifier.process()

        mock_check_exchange.assert_has_calls([
            call(conf["stackoverflow"], mock_check_time()),
            call(conf["scifi"], mock_check_time())
        ], any_order=True)

        self.assertTrue(mock_handle.called)
        mock_handle.assert_has_calls([
            call("stackoverflow", ["test"]),
            call("scifi", ["test"])
        ], any_order=True)
