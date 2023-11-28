from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint)
from flask_login import current_user, login_required
from portfolio import db
from portfolio.models import Transaction, Current_portfolio,User
from portfolio.Calculations import get_price_by_date
from portfolio.transactions.forms import TransactionForm
import datetime as dt

transactions = Blueprint('transactions', __name__)


@login_required
@transactions.route("/transaction_history")
def transaction_history():
    page = request.args.get('page',1, type=int)
    myTransactions = Transaction.query.filter_by(Transactionsmanager=current_user).order_by(Transaction.transaction_date.desc()).paginate(page=page,per_page = 15)
    myPortfolio = Current_portfolio.query.filter_by(portfolio_owner=current_user).all()
    portfolio_value = round(sum(item.sum_over_all for item in myPortfolio),2)
    return render_template('transaction_history.html', transactions=myTransactions, portfolio_value=portfolio_value)


@transactions.route("/transaction/new", methods = ['GET','POST'])
@login_required
def new_transaction():
    form = TransactionForm()
    if  form.validate_on_submit() and form.validate_quantity(quantity=form.quantity) :
        # Get the stock price on the transaction date
        priceStock = round(get_price_by_date(form.name.data, form.transaction_date.data), 2)
        form.fill_MissingValues(priceStock)
        # Check the transaction type
        if form.submitBuy.data:
            transaction_type = 'Buy'
        elif form.submitSell.data:
            transaction_type = 'Sell'
        else:
            flash("Invalid transaction type", 'danger')
            return redirect(url_for('transactions.new_transaction'))

        # Calculate price per unit and create a transaction record
        pricePerUnit = round(form.sum_over_all.data / form.quantity.data, 2)
        transaction = Transaction(
            stock_name=form.name.data,
            quantity=form.quantity.data,
            price_per_unit=pricePerUnit,
            sum_over_all=form.sum_over_all.data,
            transaction_date=form.transaction_date.data,
            transaction_type=transaction_type,
            Transactionsmanager=current_user
        )

        db.session.add(transaction)
        db.session.commit()

        user_portfolio = Current_portfolio.query.filter_by(portfolio_owner=current_user, stock_name=form.name.data).first()
        free_cash  = current_user.free_money
        if free_cash < form.sum_over_all.data and transaction_type == 'Buy':
            flash(f'You dont have this amount of money, you only have {free_cash}', 'danger')
            return redirect(url_for('transactions.new_transaction'))
        if not user_portfolio:
            user_portfolio = Current_portfolio(
                stock_name=form.name.data,
                quantity=form.quantity.data,
                buy_price=pricePerUnit,
                curr_price=pricePerUnit,
                sum_over_all=form.sum_over_all.data,
                portfolio_owner=current_user
            )

            current_user.free_money -= form.sum_over_all.data
            db.session.add(user_portfolio)
        elif transaction_type == 'Buy':
            # Use more money that you have
            user_portfolio.quantity += form.quantity.data
            user_portfolio.sum_over_all += form.sum_over_all.data
            current_user.free_money -= form.sum_over_all.data

            if user_portfolio.quantity == 0:
                user_portfolio.buy_price = 0
            else:
                # The new buy price
                user_portfolio.buy_price = round((user_portfolio.buy_price * (user_portfolio.quantity - form.quantity.data) + form.sum_over_all.data) /
                    user_portfolio.quantity, 2)
        else:
            user_portfolio.quantity -= form.quantity.data
            if user_portfolio.quantity <= 0:
                db.session.delete(user_portfolio)
            user_portfolio.curr_price = user_portfolio.sum_over_all - form.sum_over_all.data
            user_portfolio.sum_over_all -= form.sum_over_all.data
            current_user.free_money += form.sum_over_all.data

        db.session.commit()
        flash("Your Transaction has been updated", 'success')
        return redirect(url_for('stocks.My_portfolio'))
    elif request.method == 'GET':
        form.transaction_date.data = dt.datetime.now().date()

    return render_template('new_transaction.html', title='New Transaction', form=form)
