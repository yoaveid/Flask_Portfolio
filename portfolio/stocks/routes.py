
from flask import  request, render_template, url_for, redirect, Blueprint
from portfolio.models import  Current_portfolio
from flask_login import  current_user, login_required
from portfolio.Calculations import (get_portfolio_data,
                                    updatePortfolio , get_general_stock_data,get_graph_by_time, get_stock_price_change)
import datetime as dt

stocks = Blueprint('stocks', __name__)


@login_required
@stocks.route("/My_portfolio")
def My_portfolio():
    myPortfolio = Current_portfolio.query.filter_by(portfolio_owner=current_user).all()
    updatePortfolio(myPortfolio)
    portfolio_data = get_portfolio_data(myPortfolio)
    portfolio_allocation = [(stock.stock_name, stock.sum_over_all / portfolio_data['portfolio_value'] * 100) for stock in myPortfolio]
    return render_template('portfolio.html', title='My Portfolio', myPortfolio=myPortfolio, portfolio_data=portfolio_data,portfolio_allocation=portfolio_allocation)


@stocks.route("/stock/", methods=['POST','GET'])
@stocks.route("/stock/<string:stock_symbol>", methods=[ 'POST', 'GET'])
def stock(stock_symbol=None):

    search = request.args.get('search', '')
    if search == '':
        search = stock_symbol
    time_period = '1d'
    if request.method == 'POST':
        time_period = request.form.get('time-period')
        print(f'datw tie: {time_period}')
    stock_data = get_general_stock_data(search)
    print(stock_data)
    graph_data = get_graph_by_time(search, time_period=time_period)
    profits =   ((graph_data.get('prices')[-1] - graph_data.get('prices')[0] )
                    ,((graph_data.get('prices')[-1] -graph_data.get('prices')[0])/ graph_data.get('prices')[0] *100) )
    if time_period == '1d':
        profits = get_stock_price_change(search)
    print(graph_data)
    return render_template('stock.html', stock_symbol=search,stock_data=stock_data, graph_data = graph_data, profits = profits)

