import json
import requests
import time
import hashlib
from config import *
import hmac
import base64


######### in call_code need to figure out 'GET', 'POST', as well as signing #############


def call_code(data_json):
	now = int(time.time() * 1000)
	#str_to_sign = str(now) + 'GET' + '/api/v1/accounts/'
	str_to_sign = str(now) + 'POST' + '/api/v1/orders' + data_json

	signature = base64.b64encode(
		hmac.new(api_secret.encode('utf-8'), str_to_sign.encode('utf-8'), hashlib.sha256).digest())
	passphrase = base64.b64encode(hmac.new(api_secret.encode('utf-8'), api_passphrase.encode('utf-8'), hashlib.sha256).digest())
	HEADERS = {
		"KC-API-KEY": api_key,
		"KC-API-SIGN": signature,
		"KC-API-TIMESTAMP": str(now),
		"KC-API-PASSPHRASE": passphrase,
		"KC-API-KEY-VERSION": "2",
		"Content-Type": "application/json"
	}
	return HEADERS

def account_info():
	HEADERS = call_code()
	url = 'https://api.kucoin.com/api/v1/accounts/'
	response = requests.get(url, headers = HEADERS)
	print(response.status_code)
	print(response.json()['data'])

def place_order():
	
	url = 'https://api.kucoin.com/api/v1/orders'
	now = int(time.time() * 1000)
	data = {
		"clientOid":now,
		"side":"SELL",
		"symbol":"FLUX-USDT",
		"type":"LIMIT",
		"price":0.60,
		"size":5
	}
	data_json = json.dumps(data)
	HEADERS = call_code(data_json)
	response = requests.post(url, headers = HEADERS, data = data_json)
	print(response.status_code)
	print(response.json())

place_order()