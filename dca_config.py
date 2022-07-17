# clean all of this up


api_key = ""
api_secret = ""
api_passphrase = ""

symbol = "FLUX-USDT"
position_size = 17

#gridbot settings
number_buy_gridlines = 7
number_sell_gridlines = 7

#$ value
grid_size = .0125

check_orders_frequency = 1
closed_order_status = False

buy_orders = []
sell_orders = []



# DCA bot

#max_safety_orders = 5

# multipling each saftey order by 2 from the last created safety order - using * $ value - bought 1 eth, next order will buy 2, then 4
safety_order_vol_scale = 2 


# first BO % from initial price
#price_deviation_percent = .5 # this is in % so would be * .005


# calculation we need - initial_price
#safety_order_step_scale = 2

#The scale will multiply step in percents between safety orders.
#Let's assume there is a bot with a safety order price deviation 1% (we are doing .5%) and the scale is 2. Safety order prices would be:

#It's the first order, we use deviation to place it: 0 + -1% = -1%.
#last_saftey_step = 1 * price_deviation_percent (1% or * .01)

#Previous safety order step multiplied by the scale and then added to the last order percentage. The last step was 1%, the new step will be 1% * 2 = 2%. The order will be placed: -1% + -2% = -3%.
#saftey_step = 
 #   Step: 2% * 2 = 4%. Order: -3%+ -4% =-7%.

#    Step: 4% * 2 = 8%. Order: -7%+ -8% =-15%.

 #   Step: 8% * 2 = 16%. Order: -15%+ -16% =-31%.


#price_deviation_percent = .01 # 1%
#safety_order_step_scale = 2
#max_safety_orders = 5
#initial_price = 1213

last_deviation = 0



safety_order_step_scale = 2
max_safety_orders = 5
price_deviation_percent = .01 # 1% - normally run .005 or .5%

saftey_order_volume_scale = 2 # multiples orders by - in this case - * 2

    #funds = 24.80  # will need to retreive actual available balance


    # testing these right now

base_order_percent =  .03 # 5%
saftey_order_percent = .03 # 5%



    # not used yet
take_profit_percent = .003 # .3% - for now low for scalping / testing
dca_orders = [] # will need to put all order prices in here to average out to get the % TP
tp_orders = []
