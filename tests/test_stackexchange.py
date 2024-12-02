import configparser
import datetime
import unittest
from unittest.mock import patch

import httpretty

from pushoverflow.stack_exchange import check_exchange, get_stack_exchange_questions


class StackExchangeTests(unittest.TestCase):

    @patch("pushoverflow.stack_exchange.filter_questions")
    @patch("pushoverflow.stack_exchange.get_stack_exchange_questions")
    def test_check_exchange(self, get_questions, filter_questions):
        conf = configparser.ConfigParser()
        conf.read_dict({
            "stackoverflow": {
                "tags": "python, java",
                "exclude": "logging, stuff"
            }
        })
        now = datetime.datetime.now()
        get_questions.return_value = ["test"]

        check_exchange(conf["stackoverflow"], now)

        get_questions.assert_called_once_with("stackoverflow", now)
        filter_questions.assert_called_once_with(
            ["test"],
            ["python", "java"],
            ["logging", "stuff"])

    @patch("pushoverflow.stack_exchange.filter_questions")
    @patch("pushoverflow.stack_exchange.get_stack_exchange_questions")
    def test_check_exchange_no_params(self, get_questions, filter_questions):
        conf = configparser.ConfigParser()
        conf.read_dict({
            "stackoverflow": {},
        })
        now = datetime.datetime.now()
        get_questions.return_value = None

        check_exchange(conf["stackoverflow"], now)

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

        result = get_stack_exchange_questions("stackoverflow", from_time)

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

        result = get_stack_exchange_questions("stackoverflow", datetime.datetime.now())

        self.assertEqual(result, {})
