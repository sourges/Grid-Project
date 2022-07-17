# clean all of this up


api_key = ""
api_secret = ""
api_passphrase = ""

# seperate grid and dca config

symbol = "FLUX-USDT"  # for grid_bot
position_size = 17

# gridbot settings
number_buy_gridlines = 7
number_sell_gridlines = 7

# $ value
grid_size = .0125

check_orders_frequency = 1
closed_order_status = False

buy_orders = []
sell_orders = []



# DCA bot variables

safety_order_vol_scale = 2 
last_deviation = 0
safety_order_step_scale = 2
max_safety_orders = 5
price_deviation_percent = .01 # 1% - normally run .005 or .5%

saftey_order_volume_scale = 2 # multiples orders by - in this case - * 2
base_order_percent =  .03 # 3%
saftey_order_percent = .03 # 3%
take_profit_percent = .003 # .3% - for now low for scalping / testing
dca_orders = [] # will need to put all order prices in here to average out to get the % TP
tp_orders = []
