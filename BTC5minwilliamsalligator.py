
import requests
from datetime import datetime
import time

import math
import random
import ast
import hmac
import functools
import operator
import statistics

import numpy as np

import bybit


from datetime import datetime

from pprint import pprint
import gspread
from oauth2client.service_account import ServiceAccountCredentials

from googleapiclient import discovery

class HistoricalPrice(object):

    def __init__(self, host, symbol, interval, timestamp, limit, client):

        self.host = host
        self.symbol = symbol
        self.interval = interval
        self.timestamp = timestamp - (48 * 3600)
        self.limit = limit 
        self.client = client

        self.url = '{}/v2/public/kline/list'.format(self.host)


    def api_historical_response(self):
      #  r = self.client.LinearKline.LinearKline_get(symbol="BTCUSDT", interval=self.interval, limit=None, **{'from':int(self.timestamp)}).result() #IS A TYPE TUPLE FOR SOME REASON
        r = self.client.Kline.Kline_get(symbol=self.symbol, interval=self.interval, **{'from':self.timestamp}).result()
    
        for entries in r:
            self.results = entries['result']
#            print(entries)
            return self.results

    def volume(self):

        volumes = []

        for result in self.results:
            volumes.append(result['volume'])

            
        return volumes
        

    def price_close(self):

        closes = []


        for result in self.results:
            closes.append(float(result['close']))

        return closes

    def price_open(self):
        opens = [] 

        for result in self.results:
            opens.append(float(result['open']))

        return opens

    def price_high(self):
        highs = []

        for result in self.results:
            highs.append(float(result['high']))

        return highs

    def price_low(self):
        lows = []

        for result in self.results:
            lows.append(float(result['low']))

        return lows

    def candles(self):
        candlez = []

        for result in self.results:
            candlez.append((float(result['open']),float(result['close']),float(result['high']),float(result['low']))) # 1 = opens 2 = closes 3 = highs 4 = lows

        return candlez


class LivePrice(object):

    def __init__(self, host, param_str, symbol, interval, timestamp):
        self.host = host
         
        self.symbol = symbol
        
        self.url = "{}/v2/public/tickers".format(self.host)




    def price_response(self):
        r = requests.get(self.url)                  #TODO: Insert URL for response
        response = r.text
        response_dict = ast.literal_eval(response)

        return (response_dict)

    def price_dict(self):
        self.response_dict = self.price_response()
        dict_result = list(self.response_dict["result"])

   #     return dict_result

        for result in dict_result:
            if result['symbol'] == self.symbol:
                price = result['last_price']


        return float(price)



class timeStamp(object):

    def __init__(self, client):
        self.client = client
        
    def api_time_request(self):
        r = self.client.Common.Common_get().result()[0]
        time = float(r['time_now'])

 #       print('API TIME: ' + str(r))
        return int(time)

    



def get_signature(api_secret,params):
    '''Encryption Signature'''

    _val = '&'.join([str(k)+"="+str(v) for k, v in sorted(params.items()) if (k != 'sign') and (v is not None)])
    # print(_val)
    return str(hmac.new(bytes(api_secret, "utf-8"), bytes(_val, "utf-8"), digestmod="sha256").hexdigest())

class ExecuteOrder(object):

    def __init__(self,client,symbol,side,size,price,take_profit,stop_loss):

        self.client = client
        self.symbol = symbol
        self.side = side
 #       print(int(price))
  #      print(float(size))
        self.size = size #int(round(int(price) * float(size),0))
        self.price = int(round(price,0))
   #     print(self.size)

        self.take_profit = int(round(take_profit,0))

   #     print(int(self.take_profit))
    #    print(int(self.size))
     #   print(int(self.price))
        self.stop_loss = stop_loss

            
 
        

    def order(self):

        client_order = client.Order.Order_newV2(side=self.side,symbol=self.symbol,order_type="Limit",qty=int(self.size),price=int(self.price),time_in_force="ImmediateOrCancel",
                                                take_profit=int(self.take_profit),stop_loss=self.stop_loss,order_link_id=None).result()

      #  print(client.Order.Order_new(side=self.side,symbol=self.symbol,order_type="Limit",qty=self.size,price=self.price,time_in_force="PostOnly", take_profit=(self.take_profit),stop_loss=self.stop_loss).result())

  #      client_order = client.LinearOrder.LinearOrder_new(side=self.side,symbol=self.symbol,order_type="Market",qty=self.size,price=self.price,time_in_force="FillOrKill",reduce_only=False,take_profit=int(self.take_profit),stop_loss=self.stop_loss,close_on_trigger=False).result()
  #      client_order = client.LinearConditional.LinearConditional_new(stop_px=self.stop_px, side=self.side,symbol=self.symbol,order_type="Limit",qty=self.size,base_price=self.base_price, price=self.price,time_in_force="PostOnly",reduce_only=False,take_profit=int(self.take_profit),stop_loss=self.stop_loss,close_on_trigger=False).result())
  #      print(client_order)


        return (client_order)
     #   for entries in client_order:
     #       results = entries['result']
     #       order_id = results['order_id']
     #       return order_id

      #  print(type(client_order))
     #   result = client_order['result']
     #   print("ORDER RESULT: " + str(result))
     #   order_id = result['order_id']
        
        
      #  return client_order

   
 

        


class Position(object):

    def __init__(self,host,param_str,symbol):

        self.client = client
        self.host = host
        self.params = param_str
        self.symbol = symbol

        self.url = '{}/v2/private/position/list?{}'.format(self.host,self.params)
        

    def wrapper_position(self):
        previous = []
        
        if "USDT" not in self.symbol:
            try:
                r = self.client.Positions.Positions_myPosition().result()
                for entries in r:
                    results = entries['result']
                    for result in results:
                        if result['symbol'] == self.symbol:
                            if len(previous) == 0 or result['position_value'] != previous[-1]:
                                previous.append(result['position_value'])
                            return result['position_value']
            except Exception:
                if len(previous) >= 1:
                    return previous[-1]
                else:
                    return 0
                
        else:
            r = client.LinearPositions.LinearPositions_myPosition(symbol=self.symbol).result()
        #    return (r)

  #      try:
          #  for entries in r:
          #      results = entries['result']                
          #      for result in results:
          #          if result['side'] == 'Buy':
          #              if result['position_value'] == 0:
          #                  continue
          #              else:
          #                  return result['size']
          #          if result['side'] == 'Sell':
          #              if result['size'] == 0:
          #                  return result['size']
          #              else:
          #                  return result['size']
  #      except Exception:
  #          return r

        
                    
        
        
        


    def HTTP_connect_position(self):
        '''NOT IN USE'''        
        print("position host: " + str(self.host))
        print("position params: " + str(self.params))
        r = requests.get(self.url)
        response = r.text
        try:
           response_dict = ast.literal_eval(response)
           dict_result = response_dict['result']
           for result in dict_result.values():
               if result == self.symbol:
                  position_value = dict_result['position_value']
 
           if int(position_value) > 0:
                return True
           else:
                return False
 
        except Exception:
            server_time = int(response[143:156])
            recv_window = int(response[170:174])

            x = server_time - recv_window
            y = server_time + 1000

            print("Timestamp must be greater than this: " + str(server_time - recv_window))
            print("Timestamp must be less than this: " + str(server_time + 1000))

            midpoint = int((y+x)/2)

            print("MIDPOINT: " + str(midpoint))
            

       #     if server_time - recv_window <= timestamp < server_time + 1000:
        #            return timestamp

            
            
            return response

class Wallet(object):

    def __init__(self,client,host,param_str,symbol):

        self.client = client
        self.host = host
        self.params = param_str
        self.symbol = symbol

        self.url = '{}/v2/private/wallet/balance?{}'.format(self.host,self.params)

 

    def HTTP_connect_wallet(self):
        '''NOT IN USE'''
        r = requests.get(self.url)                   
        response = r.text
        try:
           response_dict = ast.literal_eval(response)
           dict_result = response_dict['result']
           for result in dict_result.keys():
                if result == self.symbol[0:3]:
                    balance = dict_result[result]['available_balance']
                
                
     #      print(response) 
           return balance
        except Exception:
            return response

    def wrapper_wallet(self):
        if "USDT" not in self.symbol:
            r = self.client.Wallet.Wallet_getRecords().result()
        else:
            r = client.Wallet.Wallet_getBalance(coin="USDT").result()
      #      return r
        try:
            if "USDT" not in self.symbol: 
                for entries in r:
                    results = entries['result']
                    data = results['data']
                    for d in data:
                        if d['coin'] == self.symbol[0:3]:
                            balance = d['wallet_balance']
                            return balance
            else:
                for entries in r:
                    results = entries['result']
                    balance = results["USDT"]
                    for balances in balance:
                        available_balance = balance['available_balance']
                        return available_balance
        except Exception:
            return r
        
    #    return "done" 
        
         
 
def SMA(closes):
    '''20 Day Simple Moving Average Calculation'''

    return sum(closes) / len(closes)


def williams_alligator(closes,smoothing):

  SUM1 = sum(closes[-(smoothing + 1):-1])
  SMMA1 = SUM1/smoothing 

  SUM2 = sum(closes[-(smoothing + 2):-2])
  SMMA2 = SUM2/smoothing
  PREVSUM = SMMA2 * smoothing 

  return (smoothing * SMMA2 - SMMA2 + closes[-1]) / smoothing




def fractals(candles):
  
  # 0 = opens 1 = closes 2 = highs 3 = lows

  middle_high = candles[-3][2] 
  middle_low = candles[-3][3]


  low_1 = candles[-5][3]
  low_2 = candles[-4][3]
  low_3 = candles[-2][3]
  low_4 = candles[-1][3]

  high_1 = candles[-5][2]
  high_2 = candles[-4][2]
  high_3 = candles[-2][2]
  high_4 = candles[-1][2]

  high = 0
  low = 0

  if (high_1 and high_2 and high_3 and high_4) < middle_high:       #Bearish 
    high = middle_high
    

  if (low_1 and low_2 and low_3 and low_4) > middle_high:         #Bullish 
    low = middle_low 


  return high, low 
    

def fibonacci(a,b,percentage):

    if a > b:
      difference = a - b
      return a - (difference * percentage)

    elif b > a:
      difference = b - a
      return b - (difference * percentage)


def ichimoku(highs,lows):

  conversion_line = (max(highs[-10:-1]) + min(lows[-10:-1])) / 2

  base_line = (max(highs[-27:-1]) + min(lows[-27:-1])) / 2

  leading_span_A = (conversion_line + base_line) / 2

  leading_span_B = (max(highs[-53:-1]) + min(lows[-53:-1])) / 2

  return leading_span_A, leading_span_B










def live_api_time():
    
    api_time = client.Common.Common_getTime().result()[0]
    for time in api_time:
        if time == "time_now":
            api_time = float(api_time["time_now"])+ 160800 #-(1*6000)
            return(api_time)


def time_period(start, end, client):

    #May 1 - August 1st Consolidation 
  

    today = datetime.today()   
    
    #january 10 - February 10 

    start_date = datetime(2020, 11, 1) #YY / MM / DD           Check file to see if theres an existing datetime and entry for latest EMA
  
    print(start_date)
    start.append(int(round(start_date.timestamp())))#+ 170200 - 9390)# * 1000)) #date in millisecond timestamp


    end_date = datetime(2021, 12, 31)

    time_stamp = timeStamp(client)
  #  api_time = time_stamp.api_time_request() + 137000

    end.append(int(round(end_date.timestamp())))# + 137000)
#    end.append(api_time)
 
    

def entry(sheet, start, row, price, side, balance):

  row.append(row[-1] + 1) 


  date = datetime.fromtimestamp(start)

  #Get corresponding cell

#  cell = sheet.cell(row[-1],1).value #row, column

  sheet.update_cell(row[-1],2, "Date: " + str(date) + " Price: " + str(price) + " Side: " + str(side))
#  sheet.update_cell(row[-1],8, "MACD: " + str(MACD_crosses[-1]))
#  sheet.update_cell(row[-1],9, "EMA12: " + str(EMA12[-1]))
#  sheet.update_cell(row[-1],10, "EMA26:  " + str(EMA26[-1]))
  sheet.update_cell(row[-1],11, "Balance: " + str(balance))


def stoploss(sheet,start,row,stop_loss,first_reduction,second_reduction, balance, temp):

  date = datetime.fromtimestamp(start)

  if first_reduction == False:
      sheet.update_cell(row[-1],6, "Date: " + str(date) + " Price: " + str(stop_loss))
      sheet.update_cell(row[-1],11, "Balance: " + str(balance))
      if temp > 1:
        sheet.update_cell(row[-1],7, "Percentage gained: " + str((temp - 1) * 100))
      elif temp < 1:
       sheet.update_cell(row[-1],7, "Percentage lost: " + str(temp * 100))
  elif first_reduction == True and second_reduction == False:
      sheet.update_cell(row[-1],7, "Date: " + str(date) + " Price: " + str(stop_loss))
      sheet.update_cell(row[-1],11, "Balance: " + str(balance))


def takeprofit(sheet, start, row, take_profit, first_reduction, second_reduction, balance):

  date = datetime.fromtimestamp(start)   

  if first_reduction == False:
      sheet.update_cell(row[-1],3, "Date: " + str(date) + " Price: " + str(take_profit))
      sheet.update_cell(row[-1],11, "Balance: " + str(balance))
  elif first_reduction == True and second_reduction == False:
      sheet.update_cell(row[-1],4, "Date: " + str(date) + " Price: " + str(take_profit))
      sheet.update_cell(row[-1],11, "Balance: " + str(balance))
  elif second_reduction == True and first_reduction == True:
      sheet.update_cell(row[-1],5, "Date: " + str(date) + " Price: " + str(take_profit))
      sheet.update_cell(row[-1],11, "Balance: " + str(balance))     


def taker_order(price,quantity,balance):

    return ((quantity/price) * 1.075)

def maker_order(price,quantity,balance):

    return ((quantity/price) * 1.025)


def trade(host, param_str, symbol, interval, timestamp, params, limit, client, api_time, api_key, signature, sheet):
    """The Actual Strategy """

    #TODO:
    #Fix Break Even entries
    #Bring 
    #Test?



    #Backtesting objects
    row = [1]
    sent_requests = 0
    start = []
    end = []

    if interval is not "D":
       minute = 60 * int(interval)
    else:
       minute  = 60 * int(interval)


    balance = 1000



    #Strategy objects

    alligator_lips = []
    alligator_teeth = []
    alligator_jaw = []
    
    
    break_even = []

    highs = []
    lows = []
    span_A = []
    span_B = []
    
    buy_trigger = False

    first_reduction = False
    second_reduction = False
    reduction2 = False


    time_period(start, end, client)

    position = False

    start = start[-1]
    end = end[-1]

    oldtime = time.time()
#    print(oldtime)
 


    while start < end:
      try:
            



          if sent_requests >= 100:
              sent_requests = sent_requests - 100 
              time.sleep(100)

          historical_price = HistoricalPrice(host, symbol, interval, start, limit, client)
          api_historical_response = historical_price.api_historical_response()
          closes = historical_price.price_close()
          opens = historical_price.price_open()
          candles = historical_price.candles()

        #  print(closes)

               
 
     

          lips = williams_alligator(closes[-6:-1],3) 
          alligator_lips.append(lips)
          teeth = williams_alligator(closes[-9:-1],5)
          alligator_teeth.append(teeth)
          jaw = williams_alligator(closes[-14:-1],8)
          alligator_jaw.append(jaw)

    


          start = start + minute
        #  print("Latest close: " + str(closes[-1]))
        #  print("Jaw: " + str(alligator_jaw[-1]))
        #  print("teeth: " + str(alligator_teeth[-1]))
        #  print("Lips: " + str(alligator_lips[-1]))
          



          if position == False:
              if closes[-1] > (alligator_lips[-1] and alligator_teeth[-1] and alligator_jaw[-1]):      #(up_cross_1 and up_cross_2) == True and closes[-1] > highs[-1]:
    #              print("long order triggered")
                  break_even[:] = []
                  first_reduction = False
                  second_reduction = False
                  side = "Buy"
                  price = closes[-1]
                  stop_loss = price - (price * 0.0125)
                  distance = price - stop_loss

                  break_even.append(price)

                  take_profit_1 = price + (distance * 2.8)
                  take_profit_2 = price + (distance * 10)
                #  take_profit_3 = price + (distance * 6)

                  reduction = price + distance
            #      reduction_2 = price + (distance * 5)          # At 5R Move stop loss to 4R 

           #       final_trailing_stop = price + (distance * 4)

#                  quantity = float((0.01 * balance) / (distance)) * price

                  quantity = float(balance)# * price 

                  taker_fee = taker_order(price,quantity,balance)
                  balance = balance - taker_fee

               #   print("Balance: " + str(balance))

                  
                  entry(sheet, start, row, price, side, balance)
                  sent_requests += 6
                  
                  position = True
                                  
                #  if position == True:
                #     buy_trigger = False 



            #  elif len(lows) > 1 and (down_cross_1 and down_cross_2) == True and closes[-1] < lows[-1]:
    #              print("Short order triggered")

              #    break_even[:] = []
              #    first_reduction = False
              #    second_reduction = False
              #    side = "Sell"
              #    price = closes[-1]

              #    break_even.append(price)
              #    stop_loss = price * 1.0125
              #    distance = stop_loss - price 

               #   take_profit_1 = price - (distance * 2) 
               #   take_profit_2 = price - (distance * 3)
               #   take_profit_3 = price - (distance * 6)

                #  reduction = price - distance
          #        reduction_2 = price - (distance * 5)          # At 5R Move stop loss to 4R
                  

         #         final_trailing_stop = price - (distance * 4)          #Price moved to after price hits 5R

                #  quantity = float((0.01 * balance) / (distance)) * price

                #  taker_fee = taker_order(price,quantity,balance)
                #  balance = balance - taker_fee
                  
                  
                 # entry(sheet, start, row, price, side, balance)
                 # sent_requests += 6
                  
                #  position = True
                                  
                #  if position == True:
                #      down_cross_1 = False
                #      down_cross_2 = False
                  

          elif position == True:
            if side == "Buy":

                if candles[-1][3] <= stop_loss:
                  taker_fee = taker_order(stop_loss,quantity,balance)
                  balance = balance - taker_fee
                  balance = balance - (balance * 0.0125)
                  temp = -420
                  stoploss(sheet,start,row,closes[-1],first_reduction,second_reduction, balance, temp)
                  sent_requests += 3
                  position = False


                if candles[-1][2] >= take_profit_1:
                  maker_fee = maker_order(stop_loss,quantity,balance)
                  balance = balance + maker_fee
                  balance = balance + (balance * 0.028)
                  temp = 420
                  stoploss(sheet,start,row,closes[-1],first_reduction,second_reduction, balance, temp)
                  sent_requests += 3
                  position = False




              #  if position == True and closes[-1] < alligator_lips[-1]:
              #    taker_fee = taker_order(stop_loss,quantity,balance)
              #    balance = balance - taker_fee

              #    if closes[-1] > break_even[-1]: 
              #      temp = ((closes[-1] - break_even[-1])/closes[-1]) + 1
              #      balance = balance * temp    # Lose 1%4
              #    elif closes[-1] < break_even[-1]:
              #      temp = ((break_even[-1] - closes[-1])/closes[-1]) 
              #      balance = balance - (balance * temp)
           #       print("Balance: " + str(balance))


               #   stoploss(sheet,start,row,closes[-1],first_reduction,second_reduction, balance, temp)
               #   sent_requests += 3
               #   position = False



                
                

                      

                      
                  
                  
              


      except Exception as e:
          print(e)
          time.sleep(100)







   # closes = historical_price.price_close()
   # print("CLOSES: " + str(closes))
   # print(len(closes))
   # time.sleep(60)

   # zero_cross = MACD(closes, MACD_crosses)
   # print(MACD_crosses)
    
#    print(len(closes))
#    volume = historical_price.volume()
#    volume_sma = SMA(volume[-20:-1])
#    print(type(volume[-1]))

#    low = historical_price.price_low()
#    high = historical_price.price_high()
#    print("Low: " + str(low))
#    print("High: " + str(high))


#    simple_moving_average = SMA(closes[-20:-1])
#    upper_band = UB(simple_moving_average,closes[-21:-1])
#    lower_band = LB(simple_moving_average,closes[-21:-1])

 #   print("Upper Band: " + str(upper_band))
 #   print("Lower Band: " + str(lower_band))

 #   print("Latest Close: " + str(closes[-1]))

  #  positions = Position(host,param_str,symbol)
  #  position = positions.wrapper_position()
  #  live_price = LivePrice(host, param_str, symbol, interval, timestamp)
   # print("POSITION: " + str(position))
    

 #   wallet = Wallet(client,host,param_str,symbol)
 #   size = wallet.wrapper_wallet()
 #   print("Balance: " + str(size))# * live_price.price_dict()))

  #  live_price = LivePrice(host, param_str, symbol, interval, timestamp)
  #  price = live_price.price_dict()
  #  print(price)


  #Record entry, stop loss, take profit, and date/time in google sheets
  #














if __name__ == "__main__":

  #GOOGLE SHEETS 
  scope = ['https://www.googleapis.com/auth/drive','https://www.googleapis.com/auth/drive.file','https://www.googleapis.com/auth/spreadsheets'] #authorization For Drive


  credentials = ServiceAccountCredentials.from_json_keyfile_name("Bybit_Bitcoin_1_Minute_Data-517ea6748c2b.json",scope)     #JSON FILE WITH Credentials

  client = gspread.authorize(credentials)   

  sheet = client.open("Alligator Indicator BTC").worksheet('Sheet28')#SHEET

#  data = sheet.get_all_records() 

  # TODO: Change code below to process the `response` dict:
# pprint(data)
  timestamp =  int(time.time()*1000) + 4000000 - 310000 #+5000
  timestamp = int(time.time()*1000) + 2500
  api_domain = {"live": "", "test": ""} 
  secret = {"live": "", "test": ""} 
  url_domain = {"live": "https://api.bybit.com", "test": "https://api-testnet.bybit.com"}

  domain = "live"
  api_key = api_domain[domain]
  host = url_domain[domain]
  api_secret = secret[domain]
  client = bybit.bybit(test=False, api_key=api_key, api_secret=api_secret)   
  limit = '5'
  symbols = ["BTCUSD","ETHUSD","EOSUSD","XPRUSD","BTCUSDT"]
  symbol = "BTCUSD"
  leverage = "1"
  interval = "240"          #timeframe
  time_stamp = timeStamp(client)
  api_time = time_stamp.api_time_request() + 122000   #3 Min = + 137000       15 min = - 6000
  print("API TIME: " + str(api_time)) 
  print("TIMESTAMP: " + str(timestamp))
  client.Positions.Positions_saveLeverage(symbol=symbol, leverage="2").result()
  params = {}
  params['api_key'] = api_domain[domain]
  params['leverage'] = leverage
  params['symbol'] = symbol
  params['timestamp'] = timestamp
  signature = get_signature(api_secret,params)
  param_str = "api_key={}&leverage={}&symbol={}&timestamp={}&sign={}".format(api_key, leverage, symbol, timestamp, signature)  # Parameter required for HTTP requests
  trade(host, param_str, symbol, interval, timestamp, params, limit, client, api_time, api_key, signature, sheet)

