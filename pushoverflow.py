#!/usr/bin/python3

import sys
import configparser
import requests, json
from datetime import date, timedelta

__version__ = "0.1"
__date__ = "2013/16/07"
__updated__ = "2013/16/07"
__author__ = "Andrew McIntosh (github.com/amcintosh)"
__copyright__ = "Copyright 2013, Andrew McIntosh"
__license__ = "GPL"

STACK_EXCHANGE_BASE_URL = "http://api.stackexchange.com/2.1"
PUSHOVER_BASE_URL = "https://api.pushover.net/1/messages.json"

def getStackExchangeQuestions(stack_exchange_site, from_date):
    '''Get new questions posted to stackexchange in past day.
    '''
    stack_url = STACK_EXCHANGE_BASE_URL + "/questions"
    
    payload = { "fromdate": fromdate, "site": stack_exchange_site}
    r = requests.get(stack_url, params=payload)
    print(r.text)	
    return r.json()

	
def sendToPushover(config):
    payload = { "title":"Test", "message":"This is a test" }
    try:
        payload["token"] = config.get("Pushover","appkey")
        payload["user"] = config.get("Pushover","userkey")
    except configparser.NoOptionError as err:
        print ("Missing properties in configuration file:", err)
        return

    requests.post(PUSHOVER_BASE_URL, data=payload)
    print("Run")	
	
	
def main(argv):
    config = configparser.ConfigParser()
    config.read('pushoverflow.ini')
    fromdate = date.today() - timedelta(minutes=time_delta)
    getStackExchangeQuestions("scifi",fromdate)
    #sendToPushover(config)

	
if __name__ == "__main__":
    main(sys.argv)