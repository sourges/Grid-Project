# testing code for DCA bot

# - to do list for 7/15

# - get 'available funds' from account - maybe 7/16
# - test main loop - as of 7/14 not enough time to see actual testing if it works

# - secondary items for 7/15 - probably for next day
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

funds = 35.59847051  # will need to retreive actual available balance


# testing these right now

base_order_percent =  .02 # 1%
saftey_order_percent = .02 # 1%

initial_order_buy_amount = funds * base_order_percent # only called once through market order
initial_safety_buy_amount = funds * saftey_order_percent

# not used yet
take_profit_percent = .003 # .3% - for now low for scalping / testing
dca_orders = [] # will need to put all order prices in here to average out to get the % TP
tp_orders = []


# initial buy - eventually from webhook

def dca_bot(initial_safety_buy_amount):
	order_amount = []
	order_cost = []

	# might also need a try / except to make sure the order is actually placed before any dca or tp are placed
	order_Id = place_market_order(round(initial_order_buy_amount,6))  # can move this round somewhere else - main issue is its different for each base - market only quoteIncrement

	order_id = order_Id['orderId']
	
	initial_price, initial_fee, order_quantity = test_fills(order_id)  # returns from market price
	last_deviation = 0

	#testing order_amount + cost for dca
	order_amount.append(order_quantity)
	order_cost.append(round(initial_order_buy_amount,6))

	# test purposes, will delete later
	print(f"price inside of dca_bot - {initial_price}")
	print(f"market buy fee - {initial_fee}")
	print(f"order quantity - {order_quantity}")

	tp_price_with_fee = ((initial_price + initial_fee) * take_profit_percent) + initial_price
	

	# print for testing purposes
	print(f"tp_price_with_fee - {tp_price_with_fee}")

	# need to figure out if i want TP to be in an array and if a SO gets excituted, add fee, calculate new tp, etc
	take_profit_order = place_limit_order(tp_price_with_fee, order_quantity, "SELL" )

	tp_orders.append(take_profit_order) # should have to ['data'] but on next buy test look at print

	print("testing - tp_orders")
	print(tp_orders)

	# ****** currently testing ************


	
	for i in range(max_safety_orders):
		deviation = price_deviation_percent + last_deviation
		deviation = round(deviation, 2)
		deviated_price = initial_price - (initial_price * deviation)
		deviated_price = round(deviated_price, 7)  # will be limit price

		base_limit_order = initial_safety_buy_amount / deviated_price # - limit needs a base order to buy (Eth in this case)

		# testing
		order_amount.append(base_limit_order)
		order_cost.append(initial_safety_buy_amount)


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
		time.sleep(1)
	return dca_orders, tp_orders, order_amount, order_cost # dca orders which have order ids in an array, tp_orders only has one in an array


def call_code(str_to_sign ,data_json=None, order_id=None):
	#print(data_json)
	#print(str_to_sign)
	now = int(time.time() * 1000)
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







# used to get order info - LIMIT ONLY - working
def get_order_info(order_id):
	url = 'https://api.kucoin.com/api/v1/orders/' + order_id
	now = int(time.time() * 1000)
	str_to_sign = str(now) + 'GET' + '/api/v1/orders/' + order_id
	data_json = None
	HEADERS = call_code(str_to_sign ,data_json, order_id)
	response = requests.get(url, headers = HEADERS)
	# print("order info method")
	# print(response.status_code)
	# print(response.json())
	return response.json()



# used to get order info - MARKET ONLY - working
def test_fills(order_id):
	url = 'https://api.kucoin.com/api/v1/fills?orderId=' + order_id
	data_json = None
	now = int(time.time() * 1000)
	str_to_sign = str(now) + 'GET' + '/api/v1/fills?orderId=' + order_id
	HEADERS = call_code(str_to_sign ,data_json, order_id)
	response = requests.get(url, headers = HEADERS)
	
	# for test purposes

	#print(response.json())
	price = response.json()['data']['items'][0]['price']
	initial_fee = response.json()['data']['items'][0]['fee']
	order_quantity = response.json()['data']['items'][0]['size']
	return float(price), float(initial_fee), float(order_quantity)

# - working
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
	str_to_sign = str(now) + 'POST' + '/api/v1/orders' + data_json
	HEADERS = call_code(str_to_sign, data_json)
	response = requests.post(url, headers = HEADERS, data = data_json)
	return response.json()['data']



# - working
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
	str_to_sign = str(now) + 'POST' + '/api/v1/orders' + data_json
	HEADERS = call_code(str_to_sign, data_json)
	response = requests.post(url, headers = HEADERS, data = data_json)
	
	# test to see if sleep can be dropped to 4
	time.sleep(5)
	print("response.json inside place_market_order")
	
	test = response.json()['data']
	print(f"test = {test}")
	
	return test # order id


# - working
def account_info():
	now = int(time.time() * 1000)
	str_to_sign = str(now) + 'GET' + '/api/v1/accounts'
	HEADERS = call_code(str_to_sign)
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



#print(f"testing - dca_orders {dca_orders}")
#print(f"testing - tp_orders {tp_orders}")



def get_order_list():
	url = 'https://api.kucoin.com/api/v1/orders?status=active'
	now = int(time.time() * 1000)
	str_to_sign = str(now) + 'GET' + '/api/v1/orders?status=active'
	HEADERS = call_code(str_to_sign)
	response = requests.get(url, headers = HEADERS)
	print(response.status_code)
	print(response.json()['data']['items'])


#get_order_list()

# once TP is hit, all SO need to be cancelled
# will not use cancel all from api due to other trades in progress

def cancel_orders(order_id):
	# since orders will be in an array, will make a 'for' loop to cycle through oderID and delete
	url = 'https://api.kucoin.com/api/v1/orders/' + order_id
	now = int(time.time() * 1000)
	str_to_sign = str(now) + 'DELETE' + '/api/v1/orders/' + order_id
	data_json = None
	HEADERS = call_code(str_to_sign, data_json, order_id)
	response = requests.delete(url, headers = HEADERS)




# main loop here

dca_orders, tp_orders, order_amount, order_cost = dca_bot(initial_safety_buy_amount)  # - main for now

# for testing purpose
count = 1 


# total cost / total amount

total_order_cost = order_cost[0]
total_order_amount = order_amount[0]

# just for test, will delete later
average_cost = order_cost[0] / order_amount[0]
print(f"testing average cost - {average_cost}")

# keep
del order_cost[0]
del order_amount[0]


while True:

	# if the tp has been filled, delete all dca orders
	for tp_order in tp_orders:  # is this necessary if there is always only one TP?
		time.sleep(5) # needed at all?
		print("checking TP")
		order = get_order_info(tp_order['orderId'])
		print(order)
		print(f"TP status is - {order['data']['isActive']}")
		if order['data']['isActive'] == closed_order_status:
			for dca_order in dca_orders:
				print("TP HIT - CANCELLING ORDERS!!")
				cancel_orders(dca_order['orderId'])
				print(f"cancelling orderID - {dca_order['orderId']}")
				time.sleep(1)

			# quit() or some function to close program?  for now only testing 1 test at a time and not 2+

		# close all dca orders - this currently works

	print(f"testing order_amount array - {order_amount}")
	print(f"testing order_cost array - {order_cost}")

	order = get_order_info(dca_orders[0]['orderId'])

	print(f"general tp_orders test - {tp_orders[0]['orderId']}")  # testing to see if correct to cancel order

	# test try / except since 'if order['data']['isActive'] == closed_order_status' bugs out once in awhile
	
	try:
		if order['data']['isActive'] == closed_order_status:
			print(f"current count - {count} - dca order")
			count += 1
			

			total_order_cost += order_cost[0]
			total_order_amount += order_amount[0]
			average_cost = total_order_cost / total_order_amount
			del order_cost[0]
			del order_amount[0]

			cancel_orders(tp_orders[0]['orderId'])  # gave an error last time, but tp was already hit.  need to test this when DCA is hit - probably need tp_orders[0]['orderId']

			print("cancelling TP order")
			del tp_orders[0]
			print(f"empty here? - {tp_orders}")


			print(f"new order_cost after TP hit - {order_cost}")
			print(f"new order_amount after TP hit - {order_amount}")
			print(f"new average cost - {average_cost}")
			
			tp_price = (average_cost * .003) + average_cost
			print(f"TP price = {tp_price}")

			print("new TP order")
			take_profit_order = place_limit_order(tp_price, total_order_amount, "SELL" )
			print(take_profit_order)


			print("deleting 1st [0] dca order")
			del dca_orders[0]
			print("checking dca array")
			print(dca_orders)


			# new TP here
			tp_orders.append(take_profit_order)
			print(f"add new TP order to array - {tp_orders}")
	except Exception as e:
		print("request failed")
		continue






