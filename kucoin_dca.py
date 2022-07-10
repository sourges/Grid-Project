# testing code for DCA bot

# to do list
# - base_order = place_market_order() - need to get price it was bought at
# - move variables into config?


from config import *
import json
import requests
import time
import hashlib
import hmac
import base64


safety_order_step_scale = 2
max_safety_orders = 5

#initial_price = 1224.77 - moved to dca_bot()

#safey_order_volume_scale = 2 # not using yet - multiples orders by

funds = 42.20590105
base_order = .05
order = funds *.05




def dca_bot():

	# initial buy

	order_Id = place_market_order()
	time.sleep(5)
	
	order_id = order_Id['orderId']
	
	initial_price = test_fills(order_id)  # returns price
	price_deviation_percent = .01 # 1% - normally run .005 or .5%
	last_deviation = 0

	# test purposes
	print(f"price inside of dca_bot - {initial_price}")


	# ****** currently testing ************


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

		str_to_sign = str(now) + 'GET' + '/api/v1/fills?orderId=' + order_id
		
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



# for this test position_size will be taken NOT from config
# first test out a market buy order berore this place_order()


position_size1 = .001 # .0001  min ETH buy


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

def get_fills(order_id):
	print(f"testoing order id in fills - {order_id}")
	url = 'https://api.kucoin.com/api/v1/fills?orderId=' + order_id

	print(f"testing url - {url}")


	data_json = None
	HEADERS = call_code(data_json, order_id)
	response = requests.get(url, headers = HEADERS)
	print("printing inside get_fills")
	
	# errors
	print(response.content)
	print(response.json())
	return response.json()['data']



#order_id = '62cb043000ed5500017ce939'


def test_fills(order_id):
	url = 'https://api.kucoin.com/api/v1/fills?orderId=' + order_id
	print(url)
	data_json = None
	HEADERS = call_code(data_json, order_id)
	response = requests.get(url, headers = HEADERS)
	
	# for test purposes

	# print(response.json())
	price = response.json()['data']['items'][0]['price']
	# print(price)
	# print("********************************")
	return price
	

#test_fills(order_id)




	
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
	test = response.json()['data']
	print(f"test = {test}")
	return test # order id




dca_bot()


# test = get_fills('62cae739ff85ad0001f277d2')
# print("test in main")
# print(test)


# test = get_order_info(order_id = "62cadeb6399d7a000119ea9c")
# print("test in main")
# print(test)
