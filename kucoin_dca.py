# testing code for DCA bot

# to do list
# - base_order = place_market_order() - need to get price it was bought at
# - move variables into config





from config import *
import json
import requests
import time
import hashlib
import hmac
import base64

price_deviation_percent = .01 # 1%
safety_order_step_scale = 2
max_safety_orders = 5
initial_price = 1224.77
#safey_order_volume_scale = 2

funds = 42.20590105
base_order = .05
order = funds *.05


last_deviation = 0

def dca_bot():

	# initial buy

	base_order = place_market_order()
	print(base_order)


	# first testing out if initial buy works for now

	# for i in range(max_safety_orders):
	# 	yea = price_deviation_percent + last_deviation
	# 	yea = round(yea, 2)
	# 	deviated_price = initial_price - (initial_price * yea)
	# 	deviated_price = round(deviated_price, 2)
	# 	order *= 2 # this is safety_order_volume_scale
	# 	print(yea, deviated_price, order)
	# 	last_deviation = yea * safety_order_step_scale


def call_code(data_json=None, order_id=None):
	if data_json == None:
		now = int(time.time() * 1000)
		#str_to_sign = str(now) + 'GET' + '/api/v1/orders?status=active'
		str_to_sign = str(now) + 'GET' + '/api/v1/orders/' + order_id
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



# for this test position_size will be taken NOT from config
# first test out a market buy order berore this place_order()


position_size1 = .001 # .0001  min ETH buy

# could possibly delete this

# def place_order(price, position_size1, side): 
# 	# is position_size needed for an arguement if its coming from config

# 	url = 'https://api.kucoin.com/api/v1/orders'
# 	now = int(time.time() * 1000)
# 	data = {
# 		"clientOid":now,    # client, side, size, and symbol are required
# 		"side":side,
# 		"symbol":"ETH-USDT",
# 		"type":"MARKET",
# 		"price":price,    # market order does not need price
# 		"size":position_size1
# 	}
# 	data_json = json.dumps(data)
# 	HEADERS = call_code(data_json)
# 	response = requests.post(url, headers = HEADERS, data = data_json)
# 	print(response.status_code)
# 	print(response.json())
# 	return response.json()
	
	
def place_market_order():

	url = 'https://api.kucoin.com/api/v1/orders'
	now = int(time.time() * 1000)
	data = {
		"clientOid":now,    # client, side, size, type, and symbol are required
		"side":"BUY",
		"symbol":"ETH-USDT",
		"type":"MARKET",
		#"price":price,    # market order does not need price
		"size":position_size1
	}

	data_json = json.dumps(data)
	HEADERS = call_code(data_json)
	response = requests.post(url, headers = HEADERS, data = data_json)
	print(response.status_code)
	print("response.json inside place_market_order")
	print(response.json())
	return response.json()


dca_bot()