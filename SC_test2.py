from config import *
import time
import requests
import json

BASE_URL = 'https://stakecube.io/api/v2'
HEADERS = {"Content-Type": "application/x-www-form-urlencoded;charset=utf-8", "X-API-KEY": KEY}


### calculates nonce
def get_timestamp():
    return int(time.time() * 1000)

nonce = get_timestamp()



def get_rate_limits():
	response = requests.get('https://stakecube.io/api/v2/system/rateLimits')
	print(response.json())

get_rate_limits()