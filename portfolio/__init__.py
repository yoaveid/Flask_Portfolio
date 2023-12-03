
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from portfolio.config import Config



db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'

mail = Mail()

def create_app(config_class= config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    """
    Only run this code if it is the first time you run the application.
    This code will create the DB for the application """
    """
    with app.app_context():
        db.create_all()
        db.session.commit()
    """
    bcrypt.init_app(app)
    login_manager.init_app(app)

    from portfolio.users.routes import users
    from portfolio.transactions.routes import transactions
    from portfolio.main.routes import main
    from portfolio.stocks.routes import stocks
    from portfolio.errors.handlers import errors
    app.register_blueprint(users)
    app.register_blueprint(transactions)
    app.register_blueprint(main)
    app.register_blueprint(stocks)
    app.register_blueprint(errors)
    return app
