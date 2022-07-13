# testing code for DCA bot

# to do list for 7/13
# - place orders for each dca - currently variables are ready, just need to put the order together - done
# - call_code() need a change, probably use call_code(str_to_sign , data_json=None, order_id=None) for now even tho it looks horrible
# - if call_code() update works, then update the grid bot code as well
# - start thinking of a function that will find out - priceIncrement + baseMinSize for base order - for limit at least - see what difference market does - symbol_list has this, see if you can
#   just call one at a time
# - priceIncrement + baseMinSize would be used to round() everything


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

funds = 38.19664711  # will need to retreive actual available balance


# testing these right now

base_order_percent =  .01 # 1%
saftey_order_percent = .01 # 1%

initial_order_buy_amount = funds * base_order_percent # only called once through market order
initial_safety_buy_amount = funds * saftey_order_percent

# not used yet
take_profit_percent = .003 # .3% - for now low for scalping / testing
dca_orders = [] # will need to put all order prices in here to average out to get the % TP
tp_orders = []


# initial buy - eventually from webhook

def dca_bot(initial_safety_buy_amount):

	# might also need a try / except to make sure the order is actually placed before any dca or tp are placed
	order_Id = place_market_order(round(initial_order_buy_amount,6))  # can move this round somewhere else - main issue is its different for each base - market only quoteIncrement

	order_id = order_Id['orderId']
	
	initial_price, initial_fee, order_quantity = test_fills(order_id)  # returns from market price
	last_deviation = 0

	# test purposes, will delete later
	print(f"price inside of dca_bot - {initial_price}")
	print(f"market buy fee - {initial_fee}")
	print(f"order quantity - {order_quantity}")

	tp_price_with_fee = ((initial_price + initial_fee) * take_profit_percent) + initial_price

	# print for testing purposes
	print(f"tp_price_with_fee - {tp_price_with_fee}")

	# need to figure out if i want TP to be in an array and if a SO gets excituted, add fee, calculate new tp, etc
	take_profit_order = place_limit_order(tp_price_with_fee, order_quantity, "SELL" )
	tp_orders.append(take_profit_order['data'])


	# ****** currently testing ************



	for i in range(max_safety_orders):
		deviation = price_deviation_percent + last_deviation
		deviation = round(deviation, 2)
		deviated_price = initial_price - (initial_price * deviation)
		deviated_price = round(deviated_price, 7)  # will be limit price

		base_limit_order = initial_safety_buy_amount / deviated_price # - limit needs a base order to buy (Eth in this case)
		dca_buys = place_limit_order(deviated_price, base_limit_order, "BUY")
		dca_orders.append(dca_buys)

		#testing
		print(dca_orders)

		# this print is where limit buys go
		print(f"order # {i+1}")
		print(deviation, deviated_price, round(initial_safety_buy_amount,7), base_limit_order)

		initial_safety_buy_amount *= saftey_order_volume_scale 
		initial_safety_buy_amount = round(initial_safety_buy_amount, 7)

		last_deviation = deviation * safety_order_step_scale

	return dca_orders, tp_orders # dca orders which have order ids

# redo all of this

def call_code(data_json=None, order_id=None):
	if data_json == None:
		now = int(time.time() * 1000)
		#str_to_sign = str(now) + 'GET' + '/api/v1/orders?status=active'
		#str_to_sign = str(now) + 'GET' + '/api/v1/accounts'
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
	order_quantity = response.json()['data']['items'][0]['size']
	# print(price)
	# print("********************************")
	return float(price), float(initial_fee), float(order_quantity)
	

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
		"price": round(price, 2),   # eth is price increment of 2 decimal places
		"size":round(position_size,7)   # baseMinSize for ETH - 0.0001  baseIncrement - .0000001     7 deciaml places for eth-usdt
	}
	data_json = json.dumps(data)
	HEADERS = call_code(data_json)
	response = requests.post(url, headers = HEADERS, data = data_json)
	print(response.status_code)
	print(response.json())
	return response.json() # will have to do response.json()['data'] later, for now watch that the orders are correct

	
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


def account_info():
	HEADERS = call_code()
	url = 'https://api.kucoin.com/api/v1/accounts'
	response = requests.get(url, headers = HEADERS)
	print(response.status_code)
	funds = []
	#prints available balance
	for i in range(len(response.json()['data'])):
		if response.json()['data'][i]['currency'] == 'USDT':
			return response.json()['data'][i]['available'] # return USDT for now
		# if response.json()['data'][i]['balance'] > "0":  # these three line will print all balances > 0
			# print(response.json()['data'][i])  
			# funds.append(response.json()['data'][i])
	


#funds = account_info() # USDT
#print(funds)
dca_orders, tp_orders = dca_bot(initial_safety_buy_amount)  # - main for now

# main loop here