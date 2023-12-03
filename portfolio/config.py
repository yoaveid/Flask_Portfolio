import os
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY_portfolio')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = "MAIL_USER_NAME"
    MAIL_PASSWORD = "MAIL_PASSWORD"  
