#api_key = "62b88cd91481b40001786d57"
#api_secret = "9b9d4412-c646-4b35-8322-c48dffb477e2"

api_key = "62b9b514cfcfa100017e7849"
api_secret = "82a1008d-3f9c-4477-a9d6-277232e77ce7"
api_passphrase = "Redbull6Scroll!"


# seperate grid and dca config

symbol = "FLUX-USDT"  # for grid_bot
position_size = 14

# gridbot settings
number_buy_gridlines = 7
number_sell_gridlines = 7

# $ value
grid_size = .0125

check_orders_frequency = 1
closed_order_status = False # used by both

buy_orders = []
sell_orders = []



# DCA bot variables
# all updated for kucoin_dca.py

traded_pair = "SUSHI-USDT"
safety_order_vol_scale = 2 # - using?
#last_deviation = 0        # - for now wait to take out
safety_order_step_scale = 2
max_safety_orders = 1
price_deviation_percent = .01 # .5% - normally run .005 or .5%

saftey_order_volume_scale = 2 # multiples orders by - in this case - * 2
base_order_percent =  .15 # 15%
saftey_order_percent = .15 # 15%
take_profit_percent = .005 # .5% - for now low for scalping / testing


#dca_orders = [] # in config or main?
#tp_orders = []