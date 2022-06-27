import json
import requests
import time
import hashlib
from config import *
import hmac
import base64




now = int(time.time() * 1000)
data = {
		"clientOid":now,
		"side":"SELL",
		"symbol":"FLUX-USDT",
		"type":"MARKET",
		"price":0.35,
		"size":5
	}

data_json = json.dumps(data)
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
url = 'https://api.kucoin.com/api/v1/orders'
#response = requests.request('post', url, headers = HEADERS, data = data_json)


response = requests.post(url, headers = HEADERS, data = data_json)
print(response.status_code)
print(response.json())
print(str_to_sign)