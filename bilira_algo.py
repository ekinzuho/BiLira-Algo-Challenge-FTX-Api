# Ekin Zuhat Yaşar, 07/08/2022
# BiLira Algo Trader Challenge for posting FTX Market and Limit orders through RESTAPI

# Some functions are unused but still left in as I designed a decision mechanism first, later realising that I should
# not stray away from Challenge requests.

# I did some small changes in FtxClient file that I retrieved from the link below to get around some errors and add a
# function that can post market orders as that class does not have one. It's called market_order and its present in git
# "https://github.com/ftexchange/ftx/blob/master/rest/client.py"

import FtxClient
import json

# Importing FTX api and api secret keys from my local drive, modify directories accordingly
f_ftx_api = open("api_keys/ftx_api_key.txt", "r")
FTX_API_KEY = f_ftx_api.read()
f_ftx_api.close()
f_ftx_secret_api = open("api_keys/ftx_secret_api_key.txt", "r")
FTX_API_SECRET_KEY = f_ftx_secret_api.read()
f_ftx_secret_api.close()

# initialize FTX client
client = FtxClient.FtxClient(api_key=FTX_API_KEY, api_secret=FTX_API_SECRET_KEY)


# inactive function
########################################################################################################################
# is not in use, to be used if one wants to specify different functionalities between buying and selling handlers
def market_order_buy_handler(pair, side, size, asks):
    total_cost = 0
    ord_size = int(size)
    for ask in asks:
        if ord_size - ask[1] <= 0:
            total_cost = total_cost + (ask[0] * ord_size)
            break
        ord_size = ord_size - ask[1]
        total_cost = total_cost + (ask[0] * ask[1])
    return calculate_avg_price(size, total_cost)


# inactive function
########################################################################################################################
# is not in use, to be used if one wants to specify different functionalities between buying and selling handlers
def market_order_sell_handler(pair, side, size, bids):
    total_cost = 0
    ord_size = int(size)
    for bid in bids:
        if ord_size - bid[1] <= 0:
            total_cost = total_cost + (bid[0] * ord_size)
            break
        ord_size = ord_size - bid[1]
        total_cost = total_cost + (bid[0] * bid[1])
    return calculate_avg_price(size, total_cost)


# inactive function
########################################################################################################################
# decision function to be activated in case user wants to see the average cost and make decision
def handle_avg_price_decision(calc_avg_price):
    print('Calculated average price: ' + str(calc_avg_price) + '. Input y to proceed and n to exit.')
    decision = input()
    if decision == 'y':
        print('Accepted to proceed with the average price of ' + str(calc_avg_price))
        return float(calc_avg_price)
    elif decision == 'n':
        print('Aborting the purchase with the average price of ' + str(calc_avg_price))
        return False
    else:
        print('Wrongful decision entry.')
        return False


# get the pair's orderbook information into a dict form for market order calculations
def get_orderbook(pair, depth):
    market = client.get_orderbook(pair, depth)
    ob_bids = market['bids']
    ob_asks = market['asks']
    ob_dict = {
        'bids': ob_bids,
        'asks': ob_asks
    }
    return ob_dict


# calculate average cost of a single unit of base currency over quote currency
def calculate_avg_price(size, total_price):
    return float(total_price/float(size))


# calculate actual total cost of the market order
def total_cost_calculator(side, size, bids_or_asks):
    total_cost = 0
    ord_size = float(size)
    for bid_or_ask in bids_or_asks:
        # print('Order size left: ' + str(ord_size))
        if ord_size - bid_or_ask[1] <= 0:
            total_cost = total_cost + (bid_or_ask[0] * ord_size)
            break
        ord_size = ord_size - bid_or_ask[1]
        total_cost = total_cost + (bid_or_ask[0] * bid_or_ask[1])
    return calculate_avg_price(size, total_cost)


# handle total cost calculation of the order
def market_order_handler(side, size, orderbook):
    if side == 'buy':
        return total_cost_calculator(side, size, orderbook['asks'])
    elif side == 'sell':
        return total_cost_calculator(side, size, orderbook['bids'])
    else:
        print('invalid side exception found in market order handler')
        return False


# start the process of handling orderbook at the time of market purchase signal
def market_order_orderbook_handler(pair, side, size):
    # some default depth value, used 100 for large order cases. Default should be 20
    depth = 100
    dict_orderbook = get_orderbook(pair, depth)
    calculated_avg_price = market_order_handler(side, size, dict_orderbook)
    return calculated_avg_price


# market order posting func
def post_market_order(pair, side, size, currency):
    calc_avg_prc = market_order_orderbook_handler(pair, side, size)
    return_dict = {
        "total": calc_avg_prc * float(size),
        "price": calc_avg_prc,
        "currency": currency
    }

    # Below line is the actual placement of market order. Comment to see the Json response regardless of exceptions.
    # Will return "Exception: Invalid size: not enough balances" on an empty FTX wallet.
    # client.market_order(pair, side, size)

    return return_dict


# limit order posting func
def post_limit_order(pair, side, price, size, iceberg, currency):
    return_dict = []
    for order in range(1, iceberg+1):
        order = {
            "Order_size": float(size/iceberg),
            "Price": price,
            "Currency": currency
        }
        return_dict.append(order),

        # Below line is the actual placement of limit order. Comment to see the Json response regardless of exceptions.
        # Will return "Exception: Not enough balances" on an empty FTX wallet.
        # client.place_order(pair, side, price, float(size/iceberg))

    return return_dict


# main function
def main_handler():

    # specification over json inputs were not detailed, so some rows below are subject to change
    # this is how I stored the request file for ease of use and speed purposes.
    f_req = open("json_requests/market_request.json", "r")
    request = json.load(f_req)
    f_req.close()

    # wanted to print the json request every time to be able to process myself
    print(request)

    # given algo challenge document had lowercase action for market, uppercase Action for limit orders
    # this if checks the fact that requested order is market order.
    if 'action' in request:
        order_pair = ''
        order_size = 0
        order_side = request['action']

        # below handling is very unnecessary and amateur but was fitting the use at hand so there it goes
        if request['quote_currency'] == 'USD':
            order_pair = request['base_currency'] + '/' + request['quote_currency']
            order_size = float(request['amount'])
        elif request['base_currency'] == 'USD':
            order_pair = request['quote_currency'] + '/' + request['base_currency']
            mkt = client.get_single_market(order_pair)
            order_size = float(request['amount'])/mkt['last']

        # create return dict object
        ret_dict = post_market_order(order_pair,
                                     order_side,
                                     order_size,
                                     request['quote_currency'])

        # add necessary currency
        ret_dict['currency'] = request['quote_currency']
        if request['base_currency'] == 'USD':
            mkt = client.get_single_market(order_pair)
            ret_dict['total'] = order_size
            ret_dict['price'] = float(1/mkt['last'])
        print(ret_dict)

    # given algo challenge document had lowercase action for market, uppercase Action for limit orders
    # this if checks the fact that the request is a limit order
    elif 'Action' in request:
        order_pair = ''
        order_size = 0
        order_side = request['Action']
        order_price = request['Price']
        order_iceberg = request['Number_of_iceberg_order']

        # below handling is very unnecessary and amateur but was fitting the use at hand so there it goes
        if request['Quote_currency'] == 'USD':
            order_pair = request['Base_currency'] + '/' + request['Quote_currency']
            order_size = float(request['Amount'])
        elif request['Base_currency'] == 'USD':
            order_pair = request['Quote_currency'] + '/' + request['Base_currency']
            mkt = client.get_single_market(order_pair)
            order_size = float(request['Amount']) / mkt['last']

        ret_dict = post_limit_order(order_pair,
                                    order_side,
                                    order_price,
                                    order_size,
                                    order_iceberg,
                                    request['Quote_currency'])
        print(ret_dict)


# initialize everything
main_handler()
