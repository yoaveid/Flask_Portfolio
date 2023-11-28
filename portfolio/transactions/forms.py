from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, DateField, FloatField
from wtforms.validators import DataRequired,Optional
from flask import flash
import datetime as dt



class TransactionForm(FlaskForm):

    name = StringField('Name', validators=[DataRequired()])
    quantity = FloatField('Quantity Of Stocks', validators= [Optional()])
    sum_over_all = FloatField('Money over all', validators= [Optional()])
    transaction_date = DateField('Date', format='%Y-%m-%d', validators=([DataRequired()]))
    submitBuy = SubmitField('Buy')
    submitSell = SubmitField('Sell')

    def validate_quantity(self, quantity):
        if quantity.data is None and self.sum_over_all.data is None:
            flash('Invalid Please enter quantity or money over all', 'danger')
            return False
        elif quantity.data is not None and self.sum_over_all.data is not None:
            flash('Fill only one of Quantity or Money over all', 'danger')
            return False

        return True

    def validate_sum_over_all(self, sum_over_all):
        if self.sum_over_all.data is not None and self.quantity.data is not None:
            flash('Fill only one of Quantity or Money over all','danger')


    def validate_transaction_date(self, transaction_date):
        if transaction_date.data > dt.date.today():
            flash('You cannot choose a future date','danger')


    def fill_MissingValues(self, price_stock):
        if not self.sum_over_all.data:
            self.sum_over_all.data = price_stock*self.quantity.data
        elif not self.quantity.data:
            self.quantity.data = round(self.sum_over_all.data/price_stock, 5)