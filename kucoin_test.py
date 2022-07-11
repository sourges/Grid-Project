import json
import requests
import time
import hashlib
from config import *
import hmac
import base64
import sys



######### in call_code need to figure out 'GET', 'POST', as well as signing #############
######### test *data_json variable call between both functions, then figure out global variable calls ##########


###### eventually will need to create a class #############

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
def place_order(price, position_size, side):
	# is position_size needed for an arguement if its coming from config

	url = 'https://api.kucoin.com/api/v1/orders'
	now = int(time.time() * 1000)
	data = {
		"clientOid":now,
		"side":side,
		"symbol":"FLUX-USDT",
		"type":"LIMIT",
		"price":price,
		"size":position_size
	}
	data_json = json.dumps(data)
	HEADERS = call_code(data_json)
	response = requests.post(url, headers = HEADERS, data = data_json)
	print(response.status_code)
	print(response.json())
	return response.json()
	
	
	


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


	#return response.json()['data']['asks'][0][0], response.json()['data']['bids'][0][0]

	# returns bid price to set medium for grid
	return response.json()['data']['bids'][0][0]




# not working - get order for single order id ( not clientOid )
# must know id before use
def get_order_info(order_id):
	url = 'https://api.kucoin.com/api/v1/orders/' + order_id
	# str_to_sign = str(now) + 'GET' + '/api/v1/orders/62c19f43fc3df20001f6214c'
	data_json = None
	HEADERS = call_code(data_json, order_id)
	response = requests.get(url, headers = HEADERS)
	#print(response.status_code)
	#print(response.json())
	return response.json()




# open orders yet to fill
def get_order_list():
	url = 'https://api.kucoin.com/api/v1/orders?status=active'
	# str_to_sign = str(now) + 'GET' + '/api/v1/orders?status=active'
	HEADERS = call_code()
	response = requests.get(url, headers = HEADERS)
	print(response.status_code)
	print(response.json()['data']['items'])


#get_order_list()


def test_grid():
	current_price = get_single_ticker()
	current_price = float(current_price)
	curren_price = round(current_price, 3)
	
	# sell grid
	for i in range(number_sell_gridlines):
		price = (float(current_price) + float(grid_size * (i+1)))
		price = round(price, 3)
		order = place_order(price, position_size, side = "SELL")
		sell_orders.append(order['data'])
		#print(f"Sell orders - {sell_orders}")

	print(sell_orders)
		
	# buy grid
	for i in range(number_buy_gridlines):
		price = (float(current_price) - float(grid_size * (i+1)))
		price = round(price, 3)
		order = place_order(price, position_size, side = "BUY")
		buy_orders.append(order['data'])
		print(f"Buy orders - {buy_orders}")

	

		# test
		# order = place_order(price, position_size)
		# append to a list


test_grid()


while True:
	closed_order_ids = []
	print("checking orders")

	# put in a try, except - or at least see about being timed out

	for sell_order in sell_orders:
		order = get_order_info(sell_order['orderId'])
		print(order)

		order_info = order['data']

		if order_info['isActive'] == closed_order_status:
			closed_order_ids.append(order_info['orderId'])
			new_buy_price = order_info['price'] - grid_size
			new_buy_order = place_order(new_buy_price, position_size, "BUY")
			buy_orders.append(new_buy_order)

		time.sleep(check_orders_frequency)

	for buy_order in buy_orders:
		order = get_order_info(buy_order['orderId'])
		print(order)

		order_info = order['data']

		if order_info['isActive'] == closed_order_status:
			closed_order_ids.append(order_info['orderId'])
			new_sell_price = order_info['price'] - grid_size
			new_sell_order = place_order(new_sell_price, position_size, "SELL")
			sell_orders.append(new_sell_order)

		time.sleep(check_orders_frequency)

	
	for order_id in closed_order_ids:
		buy_orders = [buy_order for buy_order in buy_orders if buy_order['orderId'] != order_id]
		sell_orders = [sell_order for sell_order in sell_orders if sell_order['orderId'] != order_id]

#working

#asks, bids = get_single_ticker()
#print(asks, bids)


#get_all_tickers()
#get_symbols() - not an important function
#place_order()
#account_info()
#get_order_info()



