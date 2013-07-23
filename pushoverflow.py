#!/usr/bin/python

from __future__ import absolute_import, division, print_function, unicode_literals
import configparser
import requests
import argparse
import logging
import time
from datetime import datetime, timedelta

__version__ = "0.2"
__date__ = "2013/16/07"
__updated__ = "2013/20/07"
__author__ = "Andrew McIntosh (github.com/amcintosh)"
__copyright__ = "Copyright 2013, Andrew McIntosh"
__license__ = "GPL"

STACK_EXCHANGE_BASE_URL = "http://api.stackexchange.com/2.1"
PUSHOVER_BASE_URL = "https://api.pushover.net/1/messages.json"
LOGGER = None

def send_to_pushover(pushover_config, title, message, url=None, url_title=None):
    '''Send notification to Pushover'''
    payload = { "title": title, "message": message }
    payload["token"] = pushover_config.get("appkey")
    payload["user"] = pushover_config.get("userkey")
    payload["priority"] = pushover_config.get("priority")
    if "device" in pushover_config:
        payload["device"] = pushover_config.get("device")
    if url:
        payload["url"] = url
        payload["url_title"] = url_title
    
    res = requests.post(PUSHOVER_BASE_URL, data=payload)
    if LOGGER and res.status_code == requests.codes.ok:
        LOGGER.debug("Sent to Pushover: %r", payload)
    elif LOGGER:
        LOGGER.warn("Failed to send to Pushover: %r", res.text)



def send_questions_to_pushover(pushover_config, exchange, questions):
    '''Send notification of new StackExchange questions to Pushover.
  	   Title will contain the exchange name and message will contain
       either the number of new questions or the title of the question
       if only one exists.
    '''
    title = "PushOverflow: " + exchange.name
    if len(questions)==1:
        message = ("New question posted: " 
                + questions[0].get("title"))
        url = questions[0].get("link")
        url_title = "Open question"
    else:
        message = str(len(questions)) + " new questions posted."
        url = ("http://" + exchange.name 
            + ".stackexchange.com/questions?sort=newest")
        url_title = "Open " + exchange.name + ".stackexchange.com"
    send_to_pushover(pushover_config, title, message, url, url_title)


def get_stack_exchange_questions(stack_exchange_site, from_date):
    '''Get new questions posted to stackexchange site since the 
       provided time.
    '''
    stack_url = STACK_EXCHANGE_BASE_URL + "/questions"
    payload = { "fromdate": int(time.mktime(from_date.timetuple())), 
                "site": stack_exchange_site}
    res = requests.get(stack_url, params=payload)
    if res.status_code != requests.codes.ok:
        if LOGGER:
            LOGGER.warn("Failed to retrieve from StackExchange: %r", res.text)
        return {}
    return res.json()	


def filter_questions(questions, tags, excluded):
    '''Takes a list of questions and filters them.
       If tags is not empty, will filter any questions that do not include one of these tags.
       If excluded is not empty, will filter any questions that include one of these tags.
    '''
    filtered_questions = []
    for question in questions.get("items"):
        question_tags = question.get("tags")
        in_tags = False
        in_excluded = False
        for tag in question_tags:
            if len(tags)==0 or tag in tags:
                in_tags = True
            if tag in excluded:
                in_excluded = True
        if in_tags and not in_excluded:
            filtered_questions.append(question)
            if LOGGER:
                LOGGER.debug("Found question: '%r'", question.get("title"))
        elif LOGGER:
            LOGGER.debug("Filtered question: '%r', with tags: %r",
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
    if LOGGER:
        LOGGER.info("check_exchange: [%r], from_date: %r", 
                    exchange.name, from_date.isoformat())
 
    questions = get_stack_exchange_questions(exchange.name, from_date)
    if questions:
        questions = filter_questions(questions, tags, excluded)
    return questions
	
	
def main():
    '''Parse arguments, configuration file, loop through exchanges.'''
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
    args = parser.parse_args()

    if (args.log_file):
        logging.basicConfig(filename=args.log_file, 
                            format='%(asctime)s - %(levelname)s: %(message)s')
        global LOGGER
        LOGGER = logging.getLogger(__name__)
        LOGGER.setLevel(logging.DEBUG)

    config = configparser.ConfigParser()
    config.read(args.config)

    from_date = None
    try:
        time_delta = int(config.get("Global","time_delta_minutes"))
        from_date = datetime.now() - timedelta(minutes=time_delta)
    except configparser.NoOptionError as err:
        print ("Missing properties in configuration file:", err)
        return

    except configparser.NoOptionError as err:
        print ("Missing properties in configuration file:", err)
        return
    for section in config.sections():
        if section == "Global" or section == "Pushover": 
            continue
        exchange = config[section]
        questions = check_exchange(exchange, from_date)
        if len(questions) > 0:
            send_questions_to_pushover(config["Pushover"], exchange, questions)

	
if __name__ == "__main__":
    main()
