import calendar
import logging

import requests

from pushoverflow import TIMEOUT

STACK_EXCHANGE_BASE_URL = "https://api.stackexchange.com/2.1"
log = logging.getLogger(__name__)


def get_stack_exchange_questions(stack_exchange_site, from_date):
    """Get new questions posted to stackexchange site since the provided time."""
    stack_url = STACK_EXCHANGE_BASE_URL + "/questions"
    payload = {
        "fromdate": calendar.timegm(from_date.utctimetuple()),
        "site": stack_exchange_site
    }
    res = requests.get(stack_url, params=payload, timeout=TIMEOUT)
    if res.status_code != requests.codes.ok:
        log.warning("Failed to retrieve from StackExchange: %s", res.text)
        return {}
    return res.json()


def filter_questions(questions, tags, excluded):
    """Takes a list of questions and filters them.

    If tags is not empty, will filter any questions that do not include one of these tags.
    If excluded is not empty, will filter any questions that include one of these tags.
    """
    filtered_questions = []
    for question in questions.get("items"):
        question_tags = question.get("tags")
        in_tags = False
        in_excluded = False
        for tag in question_tags:
            if len(tags) == 0 or tag in tags:
                in_tags = True
            if tag in excluded:
                in_excluded = True
        if in_tags and not in_excluded:
            filtered_questions.append(question)
            log.debug("Found question: '%s'", question.get("title"))
        log.debug("Filtered question: '%s', with tags: %s", question.get("title"), question_tags)
    return filtered_questions


def check_exchange(exchange, from_date):
    """Get new questions for this stackexchange site based off of filters provided
    in configuration file.
    """
    tags = excluded = []
    if exchange.get("tags"):
        tags = [x.strip() for x in exchange.get("tags").split(",")]
    if exchange.get("exclude"):
        excluded = [x.strip() for x in exchange.get("exclude").split(",")]
    log.info("check_exchange: [%s], from_date: %s", exchange.name, from_date.isoformat())

    questions = get_stack_exchange_questions(exchange.name, from_date)
    if questions:
        questions = filter_questions(questions, tags, excluded)
    return questions
