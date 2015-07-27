import unittest
import httpretty
from pushoverflow import cli


class PushoverTests(unittest.TestCase):

    def setUp(self):
        self.test_config = {
            "Pushover": {
                "appkey": "APP_KEY",
                "userkey": "USER_KEY",
                "priority": 0,
                "device": "DEVICE"
            }
        }

    @httpretty.activate
    def test_send_single_question(self):
        httpretty.register_uri(
            httpretty.POST, "https://api.pushover.net/1/messages.json",
            status=200
        )
        questions = [{"title": "A TITLE", "link": "A_LINK_SOMEWHERE"}]
        success = cli.send_questions_to_pushover(
            self.test_config["Pushover"], "TEST", questions)

        self.assertTrue(success)
        self.assertEqual(httpretty.last_request().method, "POST")
        self.assertEqual(
            httpretty.last_request().body,
            "title=PushOverflow%3A+TEST&url=A_LINK_SOMEWHERE&priority=0"
            "&token=APP_KEY&user=USER_KEY&device=DEVICE"
            "&message=New+question+posted%3A+A+TITLE&url_title=Open+question"
        )

    @httpretty.activate
    def test_send_questions(self):
        httpretty.register_uri(
            httpretty.POST, "https://api.pushover.net/1/messages.json",
            status=200
        )
        questions = [{"title": "TITLE 1", "link": "LINK_1"},
                     {"title": "TITLE 2", "link": "LINK_2"}]
        del self.test_config["Pushover"]["device"]
        success = cli.send_questions_to_pushover(
            self.test_config["Pushover"], "TEST", questions)

        self.assertTrue(success)
        self.assertEqual(httpretty.last_request().method, "POST")
        self.assertEqual(
            httpretty.last_request().body,
            "title=PushOverflow%3A+TEST"
            "&url=http%3A%2F%2FTEST.stackexchange.com%2Fquestions%3F"
            "sort%3Dnewest&priority=0&token=APP_KEY&user=USER_KEY"
            "&message=2+new+questions+posted"
            "&url_title=Open+TEST.stackexchange.com"
        )

    @httpretty.activate
    def test_failed_send_question(self):
        httpretty.register_uri(
            httpretty.POST, "https://api.pushover.net/1/messages.json",
            status=400
        )
        questions = [{"title": "A TITLE", "link": "A_LINK_SOMEWHERE"}]
        success = cli.send_questions_to_pushover(
            self.test_config["Pushover"], "TEST", questions)

        self.assertFalse(success)
