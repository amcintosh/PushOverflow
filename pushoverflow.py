#!/usr/bin/python3

import sys
import configparser
import requests
import time
from datetime import datetime, timedelta

__version__ = "0.1"
__date__ = "2013/16/07"
__updated__ = "2013/16/07"
__author__ = "Andrew McIntosh (github.com/amcintosh)"
__copyright__ = "Copyright 2013, Andrew McIntosh"
__license__ = "GPL"

STACK_EXCHANGE_BASE_URL = "http://api.stackexchange.com/2.1"
PUSHOVER_BASE_URL = "https://api.pushover.net/1/messages.json"

def send_to_pushover(pushover_config, title, message, url=None):
    '''Send notification to Pushover'''
    payload = { "title": title, "message": message }
    payload["token"] = pushover_config.get("appkey")
    payload["user"] = pushover_config.get("userkey")
    payload["priority"] = pushover_config.get("priority")
    if "device" in pushover_config:
        payload["device"] = pushover_config.get("device")
    if url:
        payload["url"] = url
    
    requests.post(PUSHOVER_BASE_URL, data=payload)
    #print("Push run: ", payload)	

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
    else:
        message = str(len(questions)) + " new questions posted."
        url = ("http://" + exchange.name 
            + ".stackexchange.com/questions?sort=newest")
    send_to_pushover(pushover_config, title, message, url)

def get_stack_exchange_questions(stack_exchange_site, from_date):
    '''Get new questions posted to stackexchange site since the 
       provided time.
    '''
    stack_url = STACK_EXCHANGE_BASE_URL + "/questions"
    payload = { "fromdate": int(time.mktime(from_date.timetuple())), 
                "site": stack_exchange_site}
    #print("payload:",payload)
    res = requests.get(stack_url, params=payload)
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
    questions = get_stack_exchange_questions(exchange.name, from_date)
    questions = filter_questions(questions, tags, excluded)
    return questions
		
def main(argv):
    config = configparser.ConfigParser()
    config.read('pushoverflow.ini')
    from_date = None
    try:
        time_delta = int(config.get("Global","time_delta_minutes"))
        from_date = datetime.utcnow() - timedelta(minutes=time_delta)
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
    main(sys.argv)
