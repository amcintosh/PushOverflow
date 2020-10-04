import configparser
import datetime
import unittest
from unittest.mock import patch

import httpretty
from pushoverflow import cli


class StackExchangeTests(unittest.TestCase):

    @patch("pushoverflow.cli.filter_questions")
    @patch("pushoverflow.cli.get_stack_exchange_questions")
    def test_check_exchange(self, get_questions, filter_questions):
        conf = configparser.ConfigParser()
        conf.read_dict({
            "stackoverflow": {"tags": "python, java",
                              "exclude": "logging, stuff"},
            })
        now = datetime.datetime.now()
        get_questions.return_value = ["test"]

        cli.check_exchange(conf["stackoverflow"], now)

        get_questions.assert_called_once_with("stackoverflow", now)
        filter_questions.assert_called_once_with(
            ["test"],
            ["python", "java"],
            ["logging", "stuff"])

    @patch("pushoverflow.cli.filter_questions")
    @patch("pushoverflow.cli.get_stack_exchange_questions")
    def test_check_exchange_no_params(self, get_questions, filter_questions):
        conf = configparser.ConfigParser()
        conf.read_dict({
            "stackoverflow": {},
            })
        now = datetime.datetime.now()
        get_questions.return_value = None

        cli.check_exchange(conf["stackoverflow"], now)

        get_questions.assert_called_once_with("stackoverflow", now)
        self.assertFalse(filter_questions.called)

    @httpretty.activate
    def test_get_questions(self):
        httpretty.register_uri(
            httpretty.GET, "http://api.stackexchange.com/2.1/questions",
            body='[{"foo": "bar"}]',
            status=200
        )
        test_params = {
            "fromdate": ["1440516360"], "site": ["stackoverflow"]
        }
        from_time = datetime.datetime(2015, 8, 25, 15, 26, 0, 0)

        result = cli.get_stack_exchange_questions("stackoverflow", from_time)

        self.assertEqual(result, [{"foo": "bar"}])
        self.assertEqual(httpretty.last_request().method, "GET")
        self.assertEqual(httpretty.last_request().querystring, test_params)

    @httpretty.activate
    def test_get_questions_fail(self):
        httpretty.register_uri(
            httpretty.GET, "http://api.stackexchange.com/2.1/questions",
            body='[{"foo": "bar"}]',
            status=401
        )

        result = cli.get_stack_exchange_questions("stackoverflow",
                                                  datetime.datetime.now())

        self.assertEqual(result, {})
