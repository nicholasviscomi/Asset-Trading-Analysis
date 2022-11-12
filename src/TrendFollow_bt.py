from util_bt import *
import matplotlib.pyplot as plt
import csv
import pandas as pd

SMOOTHING = 2

def Trend_Follow_Backtest():
    """
    Test a simple EMA trend following strategy.
    When a shorter moving average crosses up a longer one, an uptrend should be starting. 
    When a shorter moving average crosses down a longer one, a downtrend should be starting.
    """
    with open(one_hr_data_path, mode='r') as file:
        csv_file = csv.reader(file)

        contents = []
        for line in csv_file:
            contents.append(line)
        
        # used to loop through just specific years within the massive data file
        trades = []
        for year in year_ranges:
            inLongPos, inShortPos = False, False
            shortPosPrice, longPosPrice = 0.0, 0.0

            moving_pts = []
            lEMA_len, sEMA_len = 26, 12
            prev_lEMA, prev_sEMA = -1, -1

            lema_y, sema_y, candles = [], [], []
            for i in range(year_ranges[year][0], year_ranges[year][0] - (6 * 24), -1):
                # loop through contents starting at the end
                line = contents[i]
                open_, high_, low_, close_ = float(line[3]), float(line[4]), float(line[5]), float(line[6])
                curr_candle = Candle(open_, high_, low_, close_)

                if len(moving_pts) < lEMA_len: 
                    # need enough points for long EMA (guarantees enough for short EMA)
                    moving_pts.append(close_)
                    continue

                if (prev_lEMA == -1 or prev_sEMA == -1) and len(moving_pts) == lEMA_len:
                    prev_lEMA = sum(moving_pts)/lEMA_len

                    short_EMA_pts = moving_pts[14:]
                    prev_sEMA = sum(short_EMA_pts)/sEMA_len

                assert prev_sEMA != -1 and prev_lEMA != -1

                curr_lEMA = (close_ * (SMOOTHING / (1 + lEMA_len))) + prev_lEMA * (1 - (SMOOTHING / (1 + lEMA_len)))
                curr_sEMA = (close_ * (SMOOTHING / (1 + sEMA_len))) + prev_sEMA * (1 - (SMOOTHING / (1 + sEMA_len)))
                
                # I DONT THINK IT IS KEEPING THE EMA AT ONLY A CERTAIN LENGTH. MAKE SURE TO REMOVE POINTS AFTER ADDING THEM HERE
                lema_y.append(curr_lEMA)
                sema_y.append(curr_sEMA)
                candles.append(curr_candle)

                prev_lEMA, prev_sEMA = curr_lEMA, curr_sEMA

                # remove the oldest element, shift everything left, and add the most recent close
                # moving_pts = moving_pts[1:]
                # moving_pts.append(close_)

            prices = pd.DataFrame({
                "open"  : [candle.open_ for candle in candles],
                "high"  : [candle.high_ for candle in candles],
                "low"   : [candle.low_ for candle in candles],
                "close" : [candle.close_ for candle in candles]
            })
            green = prices[prices.close >= prices.open] # green candles
            red   = prices[prices.close < prices.open] # red candles
            w1, w2 = 0.4, 0.04 # width of thick part and width of extrema

            # graph green candles (x, height, width, bottom, color)
            plt.bar(green.index, green.close - green.open, w1, green.open, color='green') # thick middle part
            plt.bar(green.index, green.high  - green.close, w2, green.close, color='green') # high price
            plt.bar(green.index, green.low  - green.open, w2, green.open, color='green') # low price
            
            plt.bar(red.index, red.close - red.open, w1, red.open, color='red') # thick middle part
            plt.bar(red.index, red.high  - red.open, w2, red.open, color='red') # high price
            plt.bar(red.index, red.low   - red.close, w2, red.close, color='red') # low price

            plt.plot(lema_y, label='lEMA')
            plt.plot(sema_y, label='sEMA')
            plt.legend()
            plt.show()
                
    