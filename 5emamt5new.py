import MetaTrader5 as mt5
from datetime import datetime, timedelta
import pandas as pd
import pandas_ta as ta
import pdb
import time

# Connect to MetaTrader 5
mt5.initialize()

# Define trading parameters
symbol = "XAUUSD"
timeframe = mt5.TIMEFRAME_M5
leverage = 2
capital = 10000
lot_size = capital * leverage
stoploss_offset = 10
target_multiple = 2
period = 5
slippage = 3

# Function to calculate EMA
def calculate_ema(symbol, period, timeframe):
    # Fetch historical price data
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, 1000)
    
    # Create a DataFrame
    df = pd.DataFrame(rates)
    
    # Calculate EMA
    df['ema'] = ta.ema(df['close'], length=period)
    
    return df['ema'].iloc[-1]

# Main trading loop
while True:
    # Calculate trigger candle EMA
    ema5 = calculate_ema(symbol, period, timeframe)
    
    # Fetch current market data
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, 1)
    
    if rates is not None and len(rates) > 0:
        current_candle = rates[0]
        
        # Check if trigger candle condition is met
        if current_candle['close'] > (ema5 + 0.100):
            # Wait for the next candle
            time.sleep(3000)  # Sleep for 5 minutes (to ensure the next candle)
            
            # Fetch data for the next candle
            next_candle_rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, 1)
            
            if next_candle_rates is not None and len(next_candle_rates) > 0:
                next_candle = next_candle_rates[0]
                #pdb.set_trace()
                # Check if signal candle condition is met
                if next_candle['close'] > ema5:
                    # Calculate entry price, stoploss, and target
                    entry_price = next_candle['close']
                    stoploss = current_candle['high'] + stoploss_offset
                    target = entry_price - (stoploss - entry_price) * target_multiple
                    #pdb.set_trace()
                    
                    # Execute a market sell order
                    request = {
                            "action": mt5.ORDER_SELL,  # Sell order
                            "symbol": symbol,
                            "volume": lot_size,
                            "type": mt5.ORDER_MARKET,  # Market order
                            "price": entry_price,
                            "sl": stoploss,
                            "tp": target,
                            "deviation": slippage,
                            "magic": 123456,
                            "comment": "Sell Order",
                    }

                    # Send the order
                    order = mt5.order_send(request)
                    # order = mt5.OrderSend(symbol=symbol,
                                        #   action=mt5.ORDER_SELL,
                                        #   volume=lot_size,
                                        #   type=mt5.ORDER_MARKET,
                                        #   price=entry_price,
                                        #   slippage=3,
                                        #   stoploss=stoploss,
                                        #   takeprofit=target,
                                        #   deviation=20,
                                        #   magic=123456,
                                        #   comment="Sell Order")
                    # 
                    if order.retcode == mt5.TRADE_RETCODE_DONE:
                        print("Market Sell Order Executed")
                    else:
                        print(f"Error executing order: {order.comment}")
    
    # Check for market close (all positions should be closed)
    current_time = datetime.now()
    market_close_time = current_time.replace(hour=21, minute=0, second=0, microsecond=0)
    
    if current_time >= market_close_time:
        # Close all open positions
        positions = mt5.positions_get(symbol=symbol)
        
        for position in positions:
            mt5.OrderSend(symbol=symbol,
                          action=mt5.ORDER_CLOSE_BY,
                          position=position,
                          type=mt5.ORDER_MARKET,
                          volume=position.volume)
        
        print("All Positions Closed. End of Trading Day.")
        break

# Disconnect from MetaTrader 5
mt5.shutdown()
