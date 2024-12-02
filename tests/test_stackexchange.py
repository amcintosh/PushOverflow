import configparser
import datetime
from unittest.mock import patch

import responses

from pushoverflow.stack_exchange import check_exchange, get_stack_exchange_questions


@patch("pushoverflow.stack_exchange.filter_questions")
@patch("pushoverflow.stack_exchange.get_stack_exchange_questions")
def test_check_exchange(get_questions, filter_questions):
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
def test_check_exchange_no_params(get_questions, filter_questions):
    conf = configparser.ConfigParser()
    conf.read_dict({
        "stackoverflow": {},
    })
    now = datetime.datetime.now()
    get_questions.return_value = None

    check_exchange(conf["stackoverflow"], now)

    get_questions.assert_called_once_with("stackoverflow", now)
    assert not filter_questions.called


@responses.activate
def test_get_questions():
    responses.add(
        responses.GET,
        "https://api.stackexchange.com/2.1/questions",
        json=[{"foo": "bar"}],
        status=200
    )
    test_params = {
        "fromdate": "1440516360",
        "site": "stackoverflow"
    }
    from_time = datetime.datetime(2015, 8, 25, 15, 26, 0, 0)

    result = get_stack_exchange_questions("stackoverflow", from_time)

    assert result == [{"foo": "bar"}]
    assert responses.calls[0].request.method == "GET"
    assert responses.calls[0].request.params == test_params


@responses.activate
def test_get_questions_fail():
    responses.add(
        responses.GET,
        "https://api.stackexchange.com/2.1/questions",
        json=[{"foo": "bar"}],
        status=401
    )

    result = get_stack_exchange_questions("stackoverflow", datetime.datetime.now())

    assert result == {}
