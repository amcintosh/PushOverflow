import configparser

import httpretty
import pytest

from pushoverflow.core import Notifier


@pytest.fixture(autouse=True)
def test_config():
    config = configparser.ConfigParser()
    config.read_dict({
        "Global": {
            "check_minutes_back": 60
        },
        "Pushover": {
            "appkey": "APP_KEY",
            "userkey": "USER_KEY",
            "priority": 0,
            "device": "DEVICE"
        }
    })
    yield config


@httpretty.activate
def test_send_single_question(test_config):
    httpretty.register_uri(
        httpretty.POST, "https://api.pushover.net/1/messages.json",
        status=200
    )
    test_params = [
        "title=PushOverflow%3A+TEST", "url=A_LINK_SOMEWHERE",
        "priority=0", "token=APP_KEY", "user=USER_KEY", "device=DEVICE",
        "message=New+question+posted%3A+A+TITLE", "url_title=Open+question"
    ]

    questions = [{"title": "A TITLE", "link": "A_LINK_SOMEWHERE"}]
    notifier = Notifier(test_config)
    success = notifier.handle_questions("TEST", questions)

    assert success
    assert httpretty.last_request().method == "POST"

    body = httpretty.last_request().body
    assert len(body.rsplit(b"&")) == 8
    for param in test_params:
        assert param in str(body)


@httpretty.activate
def test_send_questions(test_config):
    httpretty.register_uri(
        httpretty.POST, "https://api.pushover.net/1/messages.json",
        status=200
    )
    test_params = [
        "title=PushOverflow%3A+TEST", "priority=0",
        "url=https%3A%2F%2FTEST.stackexchange.com%2Fquestions%3Fsort"
        "%3Dnewest", "token=APP_KEY", "user=USER_KEY",
        "message=2+new+questions+posted",
        "url_title=Open+TEST.stackexchange.com"
    ]

    questions = [
        {"title": "TITLE 1", "link": "LINK_1"},
        {"title": "TITLE 2", "link": "LINK_2"}
    ]
    del test_config["Pushover"]["device"]
    notifier = Notifier(test_config)
    success = notifier.handle_questions("TEST", questions)

    assert success
    assert httpretty.last_request().method == "POST"

    body = httpretty.last_request().body
    assert len(body.rsplit(b"&")) == 7
    for param in test_params:
        assert param in str(body)


@httpretty.activate
def test_failed_send_question(test_config):
    httpretty.register_uri(
        httpretty.POST, "https://api.pushover.net/1/messages.json",
        status=400
    )
    questions = [{"title": "A TITLE", "link": "A_LINK_SOMEWHERE"}]
    notifier = Notifier(test_config)
    success = notifier.handle_questions("TEST", questions)

    assert not success
