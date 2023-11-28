from datetime import datetime
from portfolio import db, login_manager
from flask import current_app
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    free_money = db.Column(db.Integer)
    user_transactions = db.relationship('Transaction', backref='Transactionsmanager', lazy=True)
    user_portfolio = db.relationship( 'Current_portfolio', backref='portfolio_owner', lazy=True)


    def get_rest_token(self, expires_sec =1000):
        s =Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s =Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User: {self.id}, {self.username}, email: {self.email}, password: {self.password}, {self.user_transactions} "


class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    stock_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_per_unit = db.Column(db.Float, nullable=False)
    sum_over_all = db.Column(db.Float, nullable=False)
    transaction_type = db.Column(db.String(10), nullable=False)
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __repr__(self):
        return f"Transaction('{self.stock_name}', {self.quantity}, ${self.price_per_unit}, {self.transaction_type}, {self.transaction_date})"

class Current_portfolio(db.Model):
    __tablename__ = 'Current_portfolio'

    id = db.Column(db.Integer, primary_key=True)
    stock_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    buy_price = db.Column(db.Float, nullable=False)
    curr_price = db.Column(db.Float, nullable=False)

    sum_over_all = db.Column(db.Float, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)


    def __repr__(self):
        return f"My portfolio: ('{self.stock_name}', {self.quantity},  ${self.buy_price})"
