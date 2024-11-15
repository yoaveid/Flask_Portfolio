import os
class Config:
    #SECRET_KEY = os.environ.get('SECRET_KEY_portfolio')
    SECRET_KEY = 'dummy secret key'
    SQLALCHEMY_DATABASE_URI = 'fake:///site.db'
    MAIL_SERVER = 'fake.googlemail.com'
    MAIL_PORT = 000
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = "MAIL_USER_NAME"
    MAIL_PASSWORD = "MAIL_PASSWORD"  
