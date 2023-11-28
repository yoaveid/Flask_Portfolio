from flask import render_template, request, Blueprint
from portfolio.Calculations import get_general_stock_data, get_graph_by_time, get_stock_price_change

main = Blueprint('main', __name__)

@main.route("/",methods=[ 'POST', 'GET'])
@main.route("/home",methods=[ 'POST', 'GET'])
def home():

    general_indexes = [{'Name': 'S&P  500', 'symbol':'^GSPC'},{'Name': 'Nasdaq100', 'symbol':'^NDX'}]
    all_data = []
    for index in general_indexes:
        symbol = index['symbol']
        stock_data = get_general_stock_data(symbol=symbol)  # S&P 500 index
        if stock_data!= -1:
            stock_data['Name'] = index['Name']
            all_data.append(stock_data)

    time_period = '1d'
    if request.method == 'POST':
        time_period = request.form.get('time-period')
    symbol = '^GSPC'
    graph_data = get_graph_by_time(symbol, time_period=time_period)
    profits =   ((graph_data.get('prices')[-1] - graph_data.get('prices')[0] )
                    ,((graph_data.get('prices')[-1] -graph_data.get('prices')[0])/ graph_data.get('prices')[0] *100) )
    if time_period == '1d':
        profits = get_stock_price_change(symbol)
    return render_template('Home.html' ,all_data=all_data , graph_data = graph_data,profits = profits)

@main.route("/about")
def about():
    return render_template('about.html')


