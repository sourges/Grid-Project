import json
import requests
import time
import hashlib
from config import *
import hmac
import base64
import sys


######### in call_code need to figure out 'GET', 'POST', as well as signing #############
######### test *data_json variable call between both functions, then figure out global variable calls



#will need to clean this up

def call_code(data_json=None):
	if data_json == None:
		now = int(time.time() * 1000)
		#str_to_sign = str(now) + 'GET' + '/api/v1/orders?status=active'
		str_to_sign = str(now) + 'GET' + '/api/v1/orders/62c19f43fc3df20001f6214c'
		#str_to_sign = str(now) + 'GET' + '/api/v1/accounts'
		#str_to_sign = str(now) + 'GET' + '/api/v1/market/allTickers'
		#str_to_sign = str(now) + 'GET' + '/api/v1/symbols'
	else:
		now = int(time.time() * 1000)
		str_to_sign = str(now) + 'POST' + '/api/v1/orders' + data_json
		
		print(str_to_sign)

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


# gets account info
def account_info():
	HEADERS = call_code()
	url = 'https://api.kucoin.com/api/v1/accounts'
	response = requests.get(url, headers = HEADERS)
	print(response.status_code)
	
	#prints available balance
	for i in range(len(response.json()['data'])):
		if response.json()['data'][i]['balance'] > "0":
			print(response.json()['data'][i])



# places a single trade
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
	log.append(response.json()['data'])
	print(log)
	
	


#get all symbol info - not a major function - more of a test function
def get_symbols():
	url = 'https://api.kucoin.com/api/v1/symbols'
	HEADERS = call_code()
	response = requests.get(url, headers = HEADERS)
	print(response.status_code)
	print(response.json())

# get all ticker info,  usdt / eth / btc / usdc - pairs into a json file
# this call might not need encryption when call_code is called, need to check
def get_all_tickers():
	url = 'https://api.kucoin.com/api/v1/market/allTickers'
	HEADERS = call_code()
	response = requests.get(url, headers = HEADERS)
	
	print(response.status_code)
	print(response.json()['data']['ticker'])
	
	filename = 'tickers.json'
	with open(filename, 'w') as f:
		json.dump(response.json(), f, indent = 4)


# gets single ticker info - must know which ticker request
def get_single_ticker():
	#must create a variable for symbol
	response = requests.get('https://api.kucoin.com/api/v1/market/orderbook/level2_20?symbol=FLUX-USDT')
	print(response.status_code)
	print("FLUX-USDT Asks - " + response.json()['data']['asks'][0][0])
	print("FLUX-USDT Bids - " + response.json()['data']['bids'][0][0])
	return response.json()['data']['asks'][0][0], response.json()['data']['bids'][0][0]




#not working - get order for single order id ( not clientOid )
def get_order_info():
	url = 'https://api.kucoin.com/api/v1/orders/62c19f43fc3df20001f6214c'
	# str_to_sign = str(now) + 'GET' + '/api/v1/orders/62c19f43fc3df20001f6214c'
	HEADERS = call_code()
	response = requests.get(url, headers = HEADERS)
	print(response.status_code)
	print(response.json())

get_order_info()



#open orders yet to fill
def get_order_list():
	url = 'https://api.kucoin.com/api/v1/orders?status=active'
	# str_to_sign = str(now) + 'GET' + '/api/v1/orders?status=active'
	HEADERS = call_code()
	response = requests.get(url, headers = HEADERS)
	print(response.status_code)
	print(response.json())

#get_order_list()

#working

#asks, bids = get_single_ticker()
#print(asks, bids)


#get_all_tickers()
#get_symbols() - not an important function
#place_order()
#account_info()
#get_order_info()

