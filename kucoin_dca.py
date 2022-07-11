# testing code for DCA bot

# to do list for 7/12
# - set up 1st TP for initial order
# - place orders for each dca 
# - clean up alot of the comments
# - clean up unused / unnessary code
# - move variables into config?
# - test if you can limit buy from 'funds' (quote currency) instead of 'size' (base currency)


from config import *
import json
import requests
import time
import hashlib
import hmac
import base64






# these will eventually be manually entered by the user

safety_order_step_scale = 2
max_safety_orders = 5
price_deviation_percent = .01 # 1% - normally run .005 or .5%

saftey_order_volume_scale = 2 # multiples orders by - in this case - * 2

funds = 30.64692739  # will need to retreive actual available balance


# testing these right now

base_order_percent =  .01 # 1%
saftey_order_percent = .01 # 1%

initial_order_buy_amount = funds * base_order_percent # need a different name that is easier to understand
initial_safety_buy_amount = funds * saftey_order_percent

# not used yet
take_profit_percent = .3 # .3 % or .003
dca_orders = [] # will need to put all order prices in here to average out to get the % TP


# initial buy - eventually from webhook

def dca_bot(initial_safety_buy_amount):

	order_Id = place_market_order(round(initial_order_buy_amount,6))  # can move this round somewhere else - main issue is its different for each base - market only quoteIncrement


	# time.sleep(5) - do i need at this point with the other sleep
	order_id = order_Id['orderId']
	
	initial_price, initial_fee = test_fills(order_id)  # returns market price
	last_deviation = 0

	# test purposes, will delete later
	print(f"price inside of dca_bot - {initial_price}")
	print(f"market buy fee - {initial_fee}")


	# ****** currently testing ************


	for i in range(max_safety_orders):
	 	deviation = price_deviation_percent + last_deviation
	 	deviation = round(deviation, 2)
	 	deviated_price = initial_price - (initial_price * deviation)
	 	deviated_price = round(deviated_price, 7)  # will be limit price

	  	
	  	# is there 'funds' call (amount of quote currency - usdt) for limit orders instead of 'size' (base currency)
		# place_limit_order(deviated_price, position_size, "BUY")


		# this print is where limit buys go
	 	print(f"order # {i+1}")
	 	print(deviation, deviated_price, initial_safety_buy_amount)

	 	initial_safety_buy_amount *= saftey_order_volume_scale 
	 	initial_safety_buy_amount = round(initial_safety_buy_amount, 7)

	 	last_deviation = deviation * safety_order_step_scale



def call_code(data_json=None, order_id=None):
	if data_json == None:
		now = int(time.time() * 1000)
		#str_to_sign = str(now) + 'GET' + '/api/v1/orders?status=active'

		str_to_sign = str(now) + 'GET' + '/api/v1/fills?orderId=' + order_id
		#str_to_sign = str(now) + 'GET' + '/api/v1/symbols'
		#str_to_sign = str(now) + 'GET' + '/api/v1/orders/' + order_id

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


# *************** test this to see if it works compared to test_fills() **********************


# def get_order_info(order_id):
# 	url = 'https://api.kucoin.com/api/v1/orders/' + order_id
# 	# str_to_sign = str(now) + 'GET' + '/api/v1/orders/62c19f43fc3df20001f6214c'
# 	data_json = None
# 	HEADERS = call_code(data_json, order_id)
# 	response = requests.get(url, headers = HEADERS)
	
# 	print("printing inside get_order_info")
# 	print(response.status_code)
# 	print(response.json())

# 	return response.json()




# use this to find out market order price


def test_fills(order_id):
	url = 'https://api.kucoin.com/api/v1/fills?orderId=' + order_id
	print(url)
	data_json = None
	HEADERS = call_code(data_json, order_id)
	response = requests.get(url, headers = HEADERS)
	
	# for test purposes

	# print(response.json())
	price = response.json()['data']['items'][0]['price']
	initial_fee = response.json()['data']['items'][0]['fee']
	# print(price)
	# print("********************************")
	return float(price), float(initial_fee)
	

#test_fills(order_id)



def place_limit_order(price, position_size, side):
	# is position_size needed for an arguement if its coming from config

	url = 'https://api.kucoin.com/api/v1/orders'
	now = int(time.time() * 1000)
	data = {
		"clientOid":now,
		"side":side,
		"symbol":"ETH-USDT",  # to be user entered
		"type":"LIMIT",
		"price": round(price, 4),
		"size":position_size
	}
	data_json = json.dumps(data)
	HEADERS = call_code(data_json)
	response = requests.post(url, headers = HEADERS, data = data_json)
	print(response.status_code)
	print(response.json())
	return response.json()

	
def place_market_order(initial_order_buy_amount):

	url = 'https://api.kucoin.com/api/v1/orders'
	now = int(time.time() * 1000)
	data = {
		"clientOid":now,    # client, side/funds, size, type, and symbol are required
		"side":"BUY",
		"symbol":"ETH-USDT",  # to bo user entered
		"type":"MARKET",
		"funds":initial_order_buy_amount
	}

	data_json = json.dumps(data)
	HEADERS = call_code(data_json)
	response = requests.post(url, headers = HEADERS, data = data_json)
	print(response.status_code)
	
	# test to see if sleep can be dropped to 4
	time.sleep(5)
	print("response.json inside place_market_order")
	
	test = response.json()['data']
	print(f"test = {test}")
	
	return test # order id



dca_bot(initial_safety_buy_amount)


# test = get_fills('62cae739ff85ad0001f277d2')
# print("test in main")
# print(test)


# test = get_order_info(order_id = "62cadeb6399d7a000119ea9c")
# print("test in main")
# print(test)
