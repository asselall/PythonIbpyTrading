from ib.opt import ibConnection,message
from time import sleep, strftime, localtime
from ib.ext.Contract import Contract
from ib.ext.Order import Order
from ib.ext.ExecutionFilter import ExecutionFilter
import exchange_info
import re
import decimal
import pandas as pd
from myib import MyIb
from security import Security
import csv
import matplotlib.animation as animation
from matplotlib import style
import matplotlib.pyplot as plt


accountNumber = "DU194566"
nextValidId = 0
bidPrice = 0
closePrice = []
dataDownload = []
fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)
def print_message_from_ib(msg):
    print(msg)
def get_next_valid_id (msg):
    global nextValidId
    nextValidId = msg.orderId
def get_bid_price (msg):
    global bidPrice
    if (msg.field == 1):
        bidPrice = msg.price
        tickerID = msg.tickerId
        dataDownload.append(bidPrice)
        closePrice.append(tickerID)

def create_bracket_order(parentOrderId,action, quantity, limitPrice, conn, contract):
        bracketOrders = []
        parentOrder = Order()
        parentOrder.m_orderId = parentOrderId
        parentOrder.m_action = action
        parentOrder.m_orderType = "MKT"
        parentOrder.m_account = accountNumber
        parentOrder.m_totalQuantity = quantity
        #parentOrder.m_lmtPrice = limitPrice
        #Set flag to 0 until all the orders have been processed
        parentOrder.m_transmit = False

        takeProfit = Order()
        takeProfit.m_orderId = parentOrder.m_orderId + 1
        if (action == 'BUY'):
            takeProfit.m_action = 'SELL'
            takeProfit.m_lmtPrice = round(limitPrice + (limitPrice / 100), 2)
            takeProfit.m_orderType = "LMT"
        else:
            takeProfit.m_action = 'BUY'
            takeProfit.m_lmtPrice = round(limitPrice - (limitPrice / 100), 2)
            takeProfit.m_orderType = "LMT"

        takeProfit.m_account = accountNumber
        takeProfit.m_totalQuantity = quantity

        takeProfit.m_parentId = parentOrderId
        # Set flag to 0 until all the orders have been processed
        takeProfit.m_transmit = False

        stopLoss = Order()
        stopLoss.m_orderId = parentOrder.m_orderId + 2
        if (action == 'BUY'):
            stopLoss.m_action = 'SELL'
            stopLoss.m_auxPrice = round(limitPrice - (limitPrice / 200), 2)
            stopLoss.m_orderType = "STP"
        else:
            stopLoss.m_action = 'BUY'
            stopLoss.m_auxPrice = round(limitPrice + (limitPrice / 200), 2)
            stopLoss.m_orderType = "STP"
        stopLoss.m_account = accountNumber
        stopLoss.m_totalQuantity = quantity
        stopLoss.m_parentId = parentOrderId
        # Set flag to 0 until all the orders have been processed
        stopLoss.m_transmit = True

        bracketOrders.append(parentOrder)
        bracketOrders.append(takeProfit)
        bracketOrders.append(stopLoss)
        #conn.placeOrder(nextValidId, contract, parentOrder)
        #conn.placeOrder(nextValidId+ 1, contract, takeProfit)
        #conn.placeOrder(nextValidId + 2, contract, stopLoss)
        #conn.reqOpenOrders()
        return bracketOrders

def make_contract(symbol, sec_type, exch, prim_exchange, curr):
        Contract.m_symbol = symbol
        Contract.m_secType = sec_type
        Contract.m_exchange = exch
        Contract.m_primaryExch = prim_exchange
        Contract.m_currency = curr
        return Contract
def request_current_price_security(contract, conn, tickerID):
    conn.reqMktData(tickerID, contract, '', False)

def cancel_request_market_date(conn, tickerID):
    conn.cancelMktData(tickerID)
    sleep(1)

def request_real_time_bars(contract, conn, tickerID):
    conn.reqRealTimeBars(tickerID, contract, '', 'BID', 0)

def cancel_request_real_time_bars(conn, tickerID):
    conn.cancelRealTimeBars(tickerID)

def historical_data_handler(msg):
    global closePrice
    print (msg.reqId, msg.date, msg.close)
    if ('finished' in str(msg.date)) == False:
        new_symbol = 'IBUS500'
        dataStr = '%s, %s, %s' % (new_symbol, msg.date, msg.close)
        newDataList = newDataList + [dataStr]
    else:
        new_symbol = 'IBUS500'
        filename = 'minutetrades' + new_symbol + '.csv'
        csvfile = open( filename,'wb')
        for item in newDataList:
            csvfile.write('{} \n'.format(item))
        csvfile.close()
        newDataList = []
        global dataDownload
        dataDownload.append(new_symbol)

def animate(i):
    ax1.clear()
    ax1.plot(closePrice, dataDownload)

def main():
    conn = ibConnection(port= 7496, clientId= 100)


    conn.registerAll(print_message_from_ib)
    conn.register (get_next_valid_id, "NextValidId")
    conn.register (get_bid_price, "TickPrice")
    conn.register(historical_data_handler, message.historicalData)
    conn.connect()
    cont = make_contract(symbol='GBP', curr='JPY', exch='IDEALPRO', prim_exchange=None, sec_type='CASH')
    request_real_time_bars(cont, conn, 1)
    sleep(20)
    cancel_request_real_time_bars(conn, 1)



    import time
    time.sleep(1)  # Simply to give the program time to print messages sent from IB
    # ordersToSend = []
    # ordersToSend = create_bracket_order(nextValidId, action= "SELL", quantity= 100, limitPrice= bidPrice, conn=conn, contract= cont)
    # for order in ordersToSend:
    #     print (order.m_orderId)
    #     conn.placeOrder(order.m_orderId, cont, order)
    #
    #
    # time.sleep(5)
    # # for order in ordersToSend:
    # #     if order.m_orderId == nextValidId:
    # #         order.m_transmit = True
    # #         conn.placeOrder(order.m_orderId, cont, order)
    # # time.sleep(2)
    # print(bidPrice)
    #
    # print(round(bidPrice - (bidPrice / 200),2))
    # filter = ExecutionFilter()
    # conn.reqExecutions(1000, filter)
    contract = Contract()
    contract.m_symbol = 'IBUS500'
    contract.m_secType = 'CFD'
    contract.m_exchange = 'SMART'
    contract.m_currency = 'USD'
    contract.m_conId = '111767871'


    #conn.reqHistoricalData(tickerId=1000, contract=contract, endDateTime='', durationStr='3 M', barSizeSetting='1 min', whatToShow='BID', useRTH=1, formatDate=1)
    #time.sleep(300)
    print (dataDownload)
    print (len(dataDownload))
    filename = 'downloaded_symbols.csv'
    csvfile = open(filename, 'wb')
    for item in dataDownload:
        csvfile.write('%s \n' % item)
    csvfile.close()
    conn.disconnect()
    print(nextValidId)


if __name__ == "__main__": main()