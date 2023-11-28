import datetime as dt
import math
import numpy as np
import yfinance as yf
from portfolio import db

def get_price_by_date(symbol, date=dt.datetime.now()):
    try:
        stock = yf.Ticker(symbol)
        # Calculate the date range for the specific date
        start_date = date - dt.timedelta(weeks=1)  # Adjust the number of days as needed
        end_date = date +dt.timedelta(days=1)
        data = stock.history(period="1d", start=start_date, end=end_date)
        if not data.empty:
            return data.iloc[-1].Close  # Assuming You buy in the close of the market
        else:
            return -1  # Return -1 if no data is available
    except Exception as e:
        return -1  # Handle exceptions and return -1 in case of an error


def get_general_stock_data(symbol, target_date=dt.datetime.now()):
    try:
        stock = yf.Ticker(symbol)
        index = symbol[0]=='^'
        if not index:
            try:
                marketCap = stock.basic_info['marketCap']
            except Exception as e:
                marketCap = 0
        # Calculate the previous trading day (one day before the target date)
        previous_day = target_date - dt.timedelta(days=7)

        # Fetch historical data for a range that includes the target date and the previous trading day
        data = stock.history(period="2d", start=previous_day, end=target_date)
        if not data.empty:
            # Extract the close prices of the target date and the previous trading day
            price = stock.basic_info['lastPrice']
            profiv_val, profit_precent = get_stock_price_change(symbol)
            stock_data = {
                'symbol': symbol,
                'open_price': data.iloc[-1]['Open'],
                'high_price': data['High'].iloc[-1],
                'low_price': data['Low'].iloc[-1],
                'curr_price': price,
                'profitValue': profiv_val,
                'profitPercent': profit_precent,

            }
            if not index:
                stock_data['market_Cap' ]= marketCap
            return stock_data
        else:
            return -1  # Return -1 if no data is available
    except Exception as e:
        raise (e)
        return -1  # Handle exceptions and return -1 in case of an error


def updatePortfolio(Portfolio):

    for item in Portfolio:
        item.curr_price = get_price_by_date(item.stock_name)
        item.sum_over_all = item.curr_price * item.quantity
        if item.quantity <= 0:
            db.session.delete(item)
            db.session.commit()
        item.profitValue = item.sum_over_all - (item.buy_price * item.quantity)
        item.profitPercent = (item.curr_price - item.buy_price ) /item.buy_price * 100
        item.change_value_today, item.change_percent_today  = get_stock_price_change(item.stock_name)

def get_portfolio_data(Portfolio):
    portfolio_value = sum(item.sum_over_all for item in Portfolio)
    portfolio_buy_value = sum(item.buy_price*item.quantity for item in Portfolio)
    portfolio_profitValue =  portfolio_value - portfolio_buy_value
    try:
        portfolio_profitPercent = ((portfolio_value - portfolio_buy_value) / portfolio_buy_value) * 100
    except Exception as e:
        portfolio_profitPercent = 0
    return {'portfolio_value': portfolio_value, 'portfolio_profitValue': portfolio_profitValue, 'portfolio_profitPercent':portfolio_profitPercent}


def get_stock_price_change(symbol):
    stock = yf.Ticker(symbol)

    if stock is not None:
        # Calculate the price change
        lastPrice = stock.basic_info['lastPrice']
        perviousClosePrice = stock.basic_info['regularMarketPreviousClose']
        if math.isnan(perviousClosePrice):
            perviousClosePrice = stock.basic_info['previousClose']
        price_change_value = lastPrice - perviousClosePrice
        price_change_percent =   (lastPrice - perviousClosePrice ) / perviousClosePrice  *100
        return price_change_value,price_change_percent
    else:
        return -1,-1  # Return -1 if no data is available


def get_graph_by_time(symbol, time_period='1y'):
    start, interval = get_end_date_by_string(time_period)
    end = dt.datetime.now()

    stock = yf.Ticker(symbol)
    # Fetch historical data within the specified date range
    data = stock.history(period = '1d', start=start, end=end, interval=interval)
    if time_period == '1d':
        last_trading_day = data.index.max().date()
        data = data[data.index.date == last_trading_day]
        dates = data.index.strftime('%H:%M').tolist()
    elif time_period == '5d':
        # Calculate the end date (last trading day)
        end_date = data.index.max().date()

        # Initialize a variable to count trading days
        trading_day_count = 0

        # Collect the last 5 trading days
        trading_days = []

        # Start with the end date and go back in time to find trading days
        current_date = end_date
        while trading_day_count < 5:
            if current_date in data.index.date:
                trading_days.append(current_date)
                trading_day_count += 1
            current_date -= dt.timedelta(days=1)
        # Filter the data to include only the last 5 trading days
        data = data[np.isin(data.index.date, trading_days)]

        dates = data.index.strftime('%d-%m %H:%M').tolist()
    else:
        dates = data.index.strftime('%Y-%m-%d').tolist()


    if 'Close' in data:
        return {
            'dates': dates,
            'prices': data['Open'].tolist()
        }
    elif 'Adj Close' in data:
        return {
            'dates': dates,
            'prices': data['Adj Close'].tolist()
        }
    else:
        return None  # Handle the case when the column name is not found in the data


def get_end_date_by_string(time_period='1y'):
    today = dt.datetime.now()
    default_interval = '1d'
    if time_period == '1d':
        return today - dt.timedelta(days=7), '5m' # return more if there is holidays
    elif time_period == '5d':
        return today - dt.timedelta(days=30), '30m'# return more if there is holidays
    elif time_period == '1m':
        return today - dt.timedelta(days=30), default_interval
    elif time_period == '6m':
        return today - dt.timedelta(days=180), default_interval
    elif time_period == 'ytd':
        start_date = dt.datetime(today.year, 1, 1)
        return start_date, default_interval
    elif time_period == '1y':
        return today - dt.timedelta(days=365), default_interval
    elif time_period == '5y':
        return today - dt.timedelta(days=1825), default_interval
    else:
        return today, '5m'  # Default to 5m interval for unknown time periods