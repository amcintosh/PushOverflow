import argparse
import calendar
import configparser
import datetime
import html
import logging
import sys

import requests

from pushoverflow import __version__

STACK_EXCHANGE_BASE_URL = "http://api.stackexchange.com/2.1"
PUSHOVER_BASE_URL = "https://api.pushover.net/1/messages.json"
log = logging.getLogger(__name__)


def send_to_pushover(pushover_config, title, message, url=None,
                     url_title=None):
    '''Send notification to Pushover'''
    payload = {"title": title, "message": message}
    payload["token"] = pushover_config.get("appkey")
    payload["user"] = pushover_config.get("userkey")
    payload["priority"] = pushover_config.get("priority")
    if "device" in pushover_config:
        payload["device"] = pushover_config.get("device")
    if url:
        payload["url"] = url
        payload["url_title"] = url_title

    res = requests.post(PUSHOVER_BASE_URL, data=payload)
    if res.status_code == requests.codes.ok:
        log.debug("Sent to Pushover: %s", payload)
        return True
    else:
        log.warning("Failed to send to Pushover: %s", res.text)
        return False


def send_questions_to_pushover(pushover_config, exchange_name, questions):
    '''Send notification of new StackExchange questions to Pushover.
       Title will contain the exchange name and message will contain
       either the number of new questions or the title of the question
       if only one exists.
    '''
    title = "PushOverflow: " + exchange_name
    if len(questions) == 1:
        message = ("New question posted: " + html.unescape(
            questions[0].get("title")))
        url = questions[0].get("link")
        url_title = "Open question"
    else:
        message = str(len(questions)) + " new questions posted"
        url = ("http://" + exchange_name
               + ".stackexchange.com/questions?sort=newest")
        url_title = "Open " + exchange_name + ".stackexchange.com"
    return send_to_pushover(pushover_config, title, message, url, url_title)


def get_stack_exchange_questions(stack_exchange_site, from_date):
    '''Get new questions posted to stackexchange site since the
       provided time.
    '''
    stack_url = STACK_EXCHANGE_BASE_URL + "/questions"
    payload = {"fromdate": calendar.timegm(from_date.utctimetuple()),
               "site": stack_exchange_site}
    res = requests.get(stack_url, params=payload)
    if res.status_code != requests.codes.ok:
        log.warning("Failed to retrieve from StackExchange: %s", res.text)
        return {}
    return res.json()


def filter_questions(questions, tags, excluded):
    '''Takes a list of questions and filters them.
       If tags is not empty, will filter any questions that do not
       include one of these tags.
       If excluded is not empty, will filter any questions that include
       one of these tags.
    '''
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
        log.debug("Filtered question: '%s', with tags: %s",
                  question.get("title"), question_tags)

    return filtered_questions


def check_exchange(exchange, from_date):
    '''Get new questions for this stackexchange site based off of
       filters provided in configuration file.
    '''
    tags = excluded = []
    if exchange.get("tags"):
        tags = [x.strip() for x in exchange.get("tags").split(",")]
    if exchange.get("exclude"):
        excluded = [x.strip() for x in exchange.get("exclude").split(",")]
    log.info("check_exchange: [%s], from_date: %s",
             exchange.name, from_date.isoformat())

    questions = get_stack_exchange_questions(exchange.name, from_date)
    if questions:
        questions = filter_questions(questions, tags, excluded)
    return questions


def parse_arguments(args=None):
    parser = argparse.ArgumentParser(
               description="Check for new StackExchange questions and notify "
                           "via Pushover")
    parser.add_argument("config",
                        metavar="config_file",
                        nargs="?",
                        default="pushoverflow.ini",
                        help="Configuration file (defaults to "
                             "'./pushoverflow.ini')")
    parser.add_argument("-v", "--verbose",
                        dest="log_file",
                        action="store",
                        const=".pushoverflow.log",
                        nargs="?",
                        help="enable logging for debug (logs to "
                             "'./.pushoverflow.log')")
    parser.add_argument('--version', action='version', version=__version__)
    return parser.parse_args(args)


def get_configuration():
    args = parse_arguments(sys.argv[1:])

    if (args.log_file):
        logging.basicConfig(filename=args.log_file,
                            format='%(asctime)s - %(levelname)s: %(message)s')
        log.setLevel(logging.DEBUG)
    else:
        logging.basicConfig(format='%(message)s')

    config = configparser.ConfigParser()
    config.read(args.config)
    return config


def get_check_time(time_delta_minutes):
    '''Here mostly for test mocking'''
    return datetime.datetime.utcnow() - datetime.timedelta(
        minutes=time_delta_minutes)


def main():
    '''Parse arguments, configuration file, loop through exchanges.'''
    config = get_configuration()
    from_date = None
    try:
        time_delta = int(config.get("Global", "time_delta_minutes"))
        from_date = get_check_time(time_delta)
        config.get("Pushover", "appkey")
        config.get("Pushover", "userkey")
    except (configparser.NoSectionError, configparser.NoOptionError) as err:
        print("Missing properties in configuration file:", err)
        return

    for section in config.sections():
        if section == "Global" or section == "Pushover":
            continue
        exchange = config[section]
        questions = check_exchange(exchange, from_date)
        if len(questions) > 0:
            send_questions_to_pushover(
                config["Pushover"], exchange.name, questions)
