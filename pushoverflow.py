#!/usr/bin/python3

import sys
import configparser
import requests, json
from datetime import datetime, timedelta

__version__ = "0.1"
__date__ = "2013/16/07"
__updated__ = "2013/16/07"
__author__ = "Andrew McIntosh (github.com/amcintosh)"
__copyright__ = "Copyright 2013, Andrew McIntosh"
__license__ = "GPL"

STACK_EXCHANGE_BASE_URL = "http://api.stackexchange.com/2.1"
PUSHOVER_BASE_URL = "https://api.pushover.net/1/messages.json"

def sendToPushover(config):
    ''' '''
    payload = { "title":"Test", "message":"This is a test" }
    try:
        payload["token"] = config.get("Pushover","appkey")
        payload["user"] = config.get("Pushover","userkey")
    except configparser.NoOptionError as err:
        print ("Missing properties in configuration file:", err)
        return

    requests.post(PUSHOVER_BASE_URL, data=payload)
    print("Push run: ", payload)	


def getStackExchangeQuestions(stack_exchange_site, from_date):
    '''Get new questions posted to stackexchange in past day.
    '''
    stack_url = STACK_EXCHANGE_BASE_URL + "/questions"
    payload = { "fromdate": int(from_date.timestamp()), "site": stack_exchange_site}
    print("payload:",payload)
    r = requests.get(stack_url, params=payload)
    return r.json()	

def filterQuestions(questions, tags, excluded):
    for question in questions.get("items"):
        print(question.get("title"))
	
def checkExchanges(config):
    from_date = None
    try:
        time_delta = int(config.get("Global","time_delta_minutes"))
        from_date = datetime.utcnow() - timedelta(minutes=time_delta)
    except configparser.NoOptionError as err:
        print ("Missing properties in configuration file:", err)
        return

    for section in config.sections():
        print(section)
        if section == "Global" or section == "Pushover": 
            continue
        exchange = config[section]
        tags = excluded = []
        if exchange.get("tags"):
            tags = exchange.get("tags").split(",")
        if exchange.get("exclude"):
            excluded = exchange.get("exclude").split(",")
        
        questions = getStackExchangeQuestions(exchange.name, from_date)
		
        filterQuestions(questions, tags, excluded)
		
		
def main(argv):
    config = configparser.ConfigParser()
    config.read('pushoverflow.ini')
    
    checkExchanges(config)
    #sendToPushover(config)

	
if __name__ == "__main__":
    main(sys.argv)