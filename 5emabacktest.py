from colorama import Fore
import pandas as pd
import pandas_ta as ta
import datetime
import pdb

watchlist = ['ADANIPORTS', 'ADANIENT', 'SBIN', 'TATASTEEL', 'BAJAJFINSV', 
             'RELIANCE', 'INFY', 'TCS', 'JSWSTEEL', 'LT', 'HCLTECH', 'TECHM', 'HDFCBANK', 
             'NTPC', 'BHARTIARTL', 'WIPRO', 'BAJFINANCE', 'INDUSINDBK', 'KOTAKBANK', 'HINDALCO', 'ULTRACEMCO', 'HDFCLIFE', 
             'BPCL', 'CIPLA', 'TATAMOTORS', 'AXISBANK', 'M&M', 'MARUTI', 'HEROMOTOCO', 'DRREDDY', 'EICHERMOT', 'COALINDIA', 'TITAN', 
             'UPL', 'HINDUNILVR', 'ITC', 'NESTLEIND', 'APOLLOHOSP', 'ICICIBANK', 'TATACONSUM', 'GRASIM', 'SUNPHARMA', 'BRITANNIA', 'BAJAJ-AUTO', 'ASIANPAINT', 'DIVISLAB', 'POWERGRID', 'SBILIFE', 'ONGC']

indicator = "ema"
ema_period = 5
timeframe = '5minutes'
leverage = 5
capital_per_trade = 10000 * leverage
sl_hit = False
target_hit = False
pnl = 0

final_result = {}
tradeno = 0

for name in watchlist:
    df = pd.read_csv(f'C:/Users/ADMIN/Desktop/py/5ema/5 minute/{name}.csv')
    df['5ema'] = ta.ema(df['close'], timeperiod=ema_period)
    df['trigger_candle_date'] = df['date'].shift(1)
    df = df.set_index(df['date'])
    df = df[90539:]

    status = {'state': None, 'buysell': None, 'name': None, 'date': None, 'entry_time': None, 'entry_price': None, 'qty': None, 'sl': None}

    for dtime, candle in df.iterrows():
        candle_date = pd.to_datetime(candle['date'])
        if candle_date.year >= 2021:
            time_before_10_am = datetime.time(9, 15) < candle_date.time() < datetime.time(10, 0)

            if time_before_10_am:
                trigger_candle = df.loc[candle['trigger_candle_date']]
                close_and_ema_movement = ((trigger_candle['close'] - trigger_candle['5ema']) / trigger_candle['close']) * 100
                trigger_candle_formed = close_and_ema_movement > 0.5
    
                signal_candle_formed = candle['low'] > candle['5ema']
                no_previous_signal = status['state'] is None
    
                if trigger_candle_formed and signal_candle_formed and no_previous_signal:
                    print(f"{Fore.YELLOW}Signal for {name} on {dtime} {Fore.WHITE}")
                    status['state'] = "ready_for_sell"
                    status['entry_price'] = candle['low']
                    status['signal_candle'] = dtime
                    status['sl'] = trigger_candle['high']
                    continue
                
                signal_confirmed = status['state'] == "ready_for_sell"
                if signal_confirmed and status['entry_price'] is not None and candle['low'] is not None:
                    low_broken = (candle['low'] < status['entry_price'])
                else:
                    low_broken = False
    
                if signal_confirmed and low_broken:
                    print(f"{Fore.RED} low is broken taking sell trade {name} on {dtime} {Fore.WHITE} \n")
                    tradeno += 1
                    status['buysell'] = "sell"
                    status['name'] = name
                    status['date'] = dtime[:10]
                    status['entry_time'] = dtime[:16]
                    status['qty'] = int(capital_per_trade / candle['close'])
                    sl_points = status['sl'] - status['entry_price']
                    status['tg'] = status['entry_price'] - (2 * sl_points)
                    status['traded'] = 'yes'
    
                    if status['traded'] == 'yes':
                        sl_hit = candle['high'] > status['sl']
                        target_hit = candle['low'] < status['sl']
                        market_over = pd.to_datetime(candle['date']).time() > datetime.time(15, 15)
                        
                        if sl_hit or target_hit or market_over:
                            if sl_hit:
                                pnl = int((status['entry_price'] - status['sl']) * status['qty'])
                                status['exit_price'] = status['sl']
                                status['pnl'] = pnl
    
                            if target_hit:
                                pnl = int((status['entry_price'] - status['tg']) * status['qty'])
                                status['exit_price'] = status['tg']
                                status['pnl'] = pnl
    
                            if market_over:
                                pnl = int((status['entry_price'] - candle['close']) * status['qty'])
                                status['exit_price'] = candle['close']
                                status['pnl'] = pnl
                                
    
                            status['exit_time'] = pd.to_datetime(candle['date']).time()
                            final_result[tradeno] = status
                            #pdb.set_trace()
                            status = {'state': None, 'buysell': None, 'name': None, 'date': None, 'entry_time': None, 'entry_price': None, 'qty': None, 'sl': None}
    
                    market_over = pd.to_datetime(candle['date']).time() > datetime.time(15, 15)
                    no_trades_taken = 'traded' not in status or status['traded'] is None
    
                    if market_over and no_trades_taken:
                        status = {'state': None, 'buysell': None, 'name': None, 'date': None, 'entry_time': None, 'entry_price': None, 'qty': None, 'sl': None}

# Convert the final result to a DataFrame and save it to a CSV file
res = pd.DataFrame(final_result).T
res.to_csv('BacktestingResult5ema.csv')
print("CSV saved successfully.")
