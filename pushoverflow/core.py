import html
import logging
from datetime import datetime, timedelta, timezone

import requests

from pushoverflow.stack_exchange import check_exchange

PUSHOVER_BASE_URL = "https://api.pushover.net/1/messages.json"
log = logging.getLogger(__name__)


class Notifier:

    def __init__(self, config):
        self.config = config

    def get_check_time(self, check_minutes_back):
        """Here mostly for test mocking"""
        return datetime.now(timezone.utc) - timedelta(minutes=check_minutes_back)

    def send_to_pushover(self, title: str, message: str, url: str, url_title: str):
        """Send notification to Pushover"""
        pushover_config = self.config["Pushover"]
        payload = {
            "title": title,
            "message": message,
            "token": pushover_config.get("appkey"),
            "user": pushover_config.get("userkey"),
            "priority": pushover_config.get("priority"),
            "url": url,
            "url_title": url_title
        }
        if "device" in pushover_config:
            payload["device"] = pushover_config.get("device")

        res = requests.post(PUSHOVER_BASE_URL, data=payload)
        if res.status_code == requests.codes.ok:
            log.debug("Sent to Pushover: %s", payload)
            return True
        else:
            log.warning("Failed to send to Pushover: %s", res.text)
            return False

    def handle_questions(self, exchange_name, questions):
        """Handle questions from a StackExchange. Send notification of questions to Pushover.
        Title will contain the exchange name and message will contain either the number of new
        questions or the title of the question if only one exists.
        """
        if len(questions) == 1:
            title = html.unescape(questions[0].get("title"))
            message = f"New question posted: {title}"
            url = questions[0].get("link")
            url_title = "Open question"
        else:
            message = f"{len(questions)} new questions posted"
            url = f"http://{exchange_name}.stackexchange.com/questions?sort=newest"
            url_title = f"Open {exchange_name}.stackexchange.com"

        return self.send_to_pushover(f"PushOverflow: {exchange_name}", message, url, url_title)

    def process(self):
        from_date = self.get_check_time(int(self.config.get("Global", "check_minutes_back")))
        for section in self.config.sections():
            if section == "Global" or section == "Pushover":
                continue
            exchange = self.config[section]
            questions = check_exchange(exchange, from_date)
            if len(questions) > 0:
                self.handle_questions(exchange.name, questions)
