# testing code for DCA bot

# - baseIncrement + quoteIncrement + priceIncrement - updated
# - clean up comments
# - current bug - if market order buys into 2 or 3 orders (partial fills), TP is only placed with just one of those orders and not the full amount

import config
import json
import requests
import time
import hashlib
import hmac
import base64
import sys



def dca_bot(initial_safety_buy_amount, funds, initial_order_buy_amount):
	order_amount, order_cost, dca_orders, tp_orders = [], [], [], []

	# might also need a try / except to make sure the order is actually placed before any dca or tp are placed

	order_Id = place_market_order(initial_order_buy_amount)
	order_id = order_Id['orderId']
	
	time.sleep(2)  # had issues before with 1 sec, seen no issues with updated code, might want to try back to 1 sec


	initial_price, initial_fee, order_quantity = test_fills(order_id)  # returns from market price
	last_deviation = 0

	#testing order_amount + cost for dca
	order_amount.append(order_quantity)
	order_cost.append(round(initial_order_buy_amount,6))

	# test purposes, will delete later
	print(f"price inside of dca_bot - {initial_price}")
	print(f"market buy fee - {initial_fee}")
	print(f"order quantity - {order_quantity}")

	tp_price_with_fee = ((initial_price + initial_fee) * config.take_profit_percent) + initial_price
	
	# print for testing purposes
	print(f"tp_price_with_fee - {tp_price_with_fee}")


	time.sleep(1)

	take_profit_order = place_limit_order(tp_price_with_fee, order_quantity, "SELL" )

	tp_orders.append(take_profit_order)

	print("testing - tp_orders")
	print(tp_orders)


	for i in range(config.max_safety_orders):
		deviation = config.price_deviation_percent + last_deviation
		deviation = round(deviation, 3)
		deviated_price = initial_price - (initial_price * deviation)
		deviated_price = round(deviated_price, 7)

		base_limit_order = initial_safety_buy_amount / deviated_price 

		order_amount.append(base_limit_order)
		order_cost.append(initial_safety_buy_amount)

		time.sleep(1) # testing
		dca_buys = place_limit_order(deviated_price, base_limit_order, "BUY")
		dca_orders.append(dca_buys)

		#testing
		print(dca_orders)
		print(f"order # {i+1}")
		print(deviation, deviated_price, round(initial_safety_buy_amount,7), base_limit_order)

		initial_safety_buy_amount *= config.saftey_order_volume_scale 
		initial_safety_buy_amount = round(initial_safety_buy_amount, 7)


		last_deviation = deviation * config.safety_order_step_scale
	return dca_orders, tp_orders, order_amount, order_cost 


def call_code(str_to_sign ,data_json=None, order_id=None):
	now = int(time.time() * 1000)
	signature = base64.b64encode(
		hmac.new(config.api_secret.encode('utf-8'), str_to_sign.encode('utf-8'), hashlib.sha256).digest())
	passphrase = base64.b64encode(hmac.new(config.api_secret.encode('utf-8'), config.api_passphrase.encode('utf-8'), hashlib.sha256).digest())
	HEADERS = {
		"KC-API-KEY": config.api_key,
		"KC-API-SIGN": signature,
		"KC-API-TIMESTAMP": str(now),
		"KC-API-PASSPHRASE": passphrase,
		"KC-API-KEY-VERSION": "2",
		"Content-Type": "application/json"
	}
	return HEADERS



def get_symbols(): 
	now = int(time.time() * 1000)
	str_to_sign = str(now) + 'GET' + '/api/v1/symbols/'
	url = f'https://api.kucoin.com/api/v1/symbols/{config.traded_pair}'
	HEADERS = call_code(str_to_sign)
	response = requests.get(url, headers = HEADERS)
	baseIncrement = len(response.json()['data']['baseIncrement'].split('.')[1])
	quoteIncrement = len(response.json()['data']['quoteIncrement'].split('.')[1])
	priceIncrement = len(response.json()['data']['priceIncrement'].split('.')[1])
	return baseIncrement, quoteIncrement, priceIncrement



# used to get order info - LIMIT ONLY - working
def get_order_info(order_id):
	url = 'https://api.kucoin.com/api/v1/orders/' + order_id
	now = int(time.time() * 1000)
	str_to_sign = str(now) + 'GET' + '/api/v1/orders/' + order_id
	data_json = None
	HEADERS = call_code(str_to_sign ,data_json, order_id)
	response = requests.get(url, headers = HEADERS)
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

	print(response.json())
	price = response.json()['data']['items'][0]['price']
	initial_fee = response.json()['data']['items'][0]['fee']
	order_quantity = response.json()['data']['items'][0]['size']
	return float(price), float(initial_fee), float(order_quantity)


# - working
def place_limit_order(price, position_size, side):
	
	url = 'https://api.kucoin.com/api/v1/orders'
	now = int(time.time() * 1000)
	data = {
		"clientOid":now,
		"side":side,
		"symbol":config.traded_pair,  
		"type":"LIMIT",
		"price": round(price, priceIncrement),   
		"size":round(position_size, baseIncrement)   
	}
	data_json = json.dumps(data)
	str_to_sign = str(now) + 'POST' + '/api/v1/orders' + data_json
	HEADERS = call_code(str_to_sign, data_json)
	response = requests.post(url, headers = HEADERS, data = data_json)

	# print for testing
	print(response.json()) 
	return response.json()['data']



# - working
def place_market_order(initial_order_buy_amount):

	url = 'https://api.kucoin.com/api/v1/orders'
	now = int(time.time() * 1000)
	data = {
		"clientOid":now,    
		"side":"BUY",
		"symbol":config.traded_pair,  
		"type":"MARKET",
		"funds":round(initial_order_buy_amount, quoteIncrement) 
	}

	data_json = json.dumps(data)
	str_to_sign = str(now) + 'POST' + '/api/v1/orders' + data_json
	HEADERS = call_code(str_to_sign, data_json)
	response = requests.post(url, headers = HEADERS, data = data_json)  
	

	print(f"market test - {response.json()}")


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
	#funds = [] # come back to this when other tokens are added
	#prints available balance
	for i in range(len(response.json()['data'])):
		if response.json()['data'][i]['currency'] == 'USDT':
			available_funds = response.json()['data'][i]['available']
			return  float(available_funds) # return USDT for now
		# if response.json()['data'][i]['balance'] > "0":  # these three line will print all balances > 0
			# print(response.json()['data'][i])  
			# funds.append(response.json()['data'][i])
	


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
	url = 'https://api.kucoin.com/api/v1/orders/' + order_id
	now = int(time.time() * 1000)
	str_to_sign = str(now) + 'DELETE' + '/api/v1/orders/' + order_id
	data_json = None
	HEADERS = call_code(str_to_sign, data_json, order_id)
	response = requests.delete(url, headers = HEADERS)



baseIncrement, quoteIncrement, priceIncrement = get_symbols() # testing


def main():
	funds = account_info()
	print(funds)

	initial_order_buy_amount = funds * config.base_order_percent # only called once through market order

	print(f"TESTING initial_order_buy_amount - {initial_order_buy_amount}")
	
	initial_safety_buy_amount = funds * config.saftey_order_percent


	time.sleep(1)  

	dca_orders, tp_orders, order_amount, order_cost = dca_bot(initial_safety_buy_amount, funds, initial_order_buy_amount)  # - main for now

	# for testing purpose
	count = 1 

	print(order_cost)
	print(order_amount)



	# total cost / total amount

	total_order_cost = order_cost[0]
	total_order_amount = order_amount[0]

	# just for test, will delete later
	average_cost = order_cost[0] / order_amount[0]
	print(f"testing average cost - {average_cost}")
	print(f"testing total_order_cost - {total_order_cost}")
	print(f"testing total_order_amount - {total_order_amount}")

	
	del order_cost[0]
	del order_amount[0]


	while True:

		# if the tp has been filled, delete all dca orders
		for tp_order in tp_orders:  # is this necessary if there is always only one TP?
			time.sleep(5) # needed at all?
			print("checking TP")
			try:
				order = get_order_info(tp_order['orderId'])
				print(order)
				print(f"TP status is - {order['data']['isActive']}")
				if order['data']['isActive'] == config.closed_order_status:   
					for dca_order in dca_orders:
						print("TP HIT - CANCELLING ORDERS!!")
						cancel_orders(dca_order['orderId'])
						print(f"cancelling orderID - {dca_order['orderId']}")
						time.sleep(1)
					sys.exit()
			except Exception as e:
				print("tp_order check status failed")
				continue
				

			# close all dca orders - this currently works

		print(f"testing order_amount array - {order_amount}")
		print(f"testing order_cost array - {order_cost}")

		time.sleep(1) 
		order = get_order_info(dca_orders[0]['orderId'])

		print(f"general tp_orders test - {tp_orders[0]['orderId']}")  # testing to see if correct to cancel order


		# try needed at all?
		
		try:
			if order['data']['isActive'] == config.closed_order_status:
				print(f"current count - {count} - dca order")
				count += 1
				

				total_order_cost += order_cost[0]
				total_order_amount += order_amount[0]
				average_cost = total_order_cost / total_order_amount
				del order_cost[0]
				del order_amount[0]


				time.sleep(1) 

				cancel_orders(tp_orders[0]['orderId'])  #  need to test this when DCA is hit - probably need tp_orders[0]['orderId'] - currently works

				print("cancelling TP order")
				del tp_orders[0]
				print(f"empty here? - {tp_orders}")


				print(f"new order_cost after TP hit - {order_cost}")
				print(f"new order_amount after TP hit - {order_amount}")
				print(f"new average cost - {average_cost}")
				
				tp_price = (average_cost * config.take_profit_percent) + average_cost
				print(f"TP price = {tp_price}")

				print("new TP order")

				time.sleep(1) 


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




if __name__ == "__main__":
	main()


