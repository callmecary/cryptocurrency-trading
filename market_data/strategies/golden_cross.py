from datetime import datetime
import pandas as pd


class GoldenCross:
    def __init__(self, **params):
        self.prices = pd.DataFrame()
        self.beta = 0
        self.is_position_opened = False
        self.opening_price = 0
        self.executed_price = 0
        self.unrealized_pnl = 0
        self.realized_pnl = 0
        self.position = 0
        self.dt_format = "%Y-%m-%dT%H:%M:%S.%fZ"

        self.qty = params["qty"]
        self.interval = params["interval"]
        self.mean_period_short = params["mean_period_short"]
        self.mean_period_long = params["mean_period_long"]
        self.buy_threshold = params["buy_threshold"]
        self.sell_threshold = params["sell_threshold"]


    def parse_data(self,data):
        if(data['type']=='ticker'):
            return data['time'],data['instrument'],data['lastBid'],data['lastAsk']


    
    def on_messgae(self,tick):
        time,instrument,bid,ask = self.parse_data(tick)
        self.tick_event(time,instrument,float(bid),float(ask))

    def tick_event(self,time,instrument,bid,ask):
        time = pd.to_datetime(time)
        midprice = (ask+bid)/2.
        self.prices.loc[time, instrument] = midprice
        print(self.prices)
        resampled_prices = self.prices.resample(self.interval).last()

        mean_short = resampled_prices.tail(
            self.mean_period_short).mean()[0]
        mean_long = resampled_prices.tail(
            self.mean_period_long).mean()[0]
        self.beta = mean_short / mean_long

        self.perform_trade_logic(self.beta)

    def perform_trade_logic(self, beta):
        if beta > self.buy_threshold:
            if not self.is_position_opened \
                    or self.position < 0:
                self.check_and_send_order(True)

        elif beta < self.sell_threshold:
            if not self.is_position_opened \
                    or self.position > 0:
                self.check_and_send_order(False)

    def check_and_send_order(self,is_true):
        if is_true:
            print('Order sent.')
        

                
