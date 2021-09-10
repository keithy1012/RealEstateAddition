import os
class Config:
    SECRET_KEY = 'fjkse238cfduwku4h489fhdjksnc49chdj33fjgbw'
    SQLALCHEMY_DATABASE_URI ='sqlite:///site.db'
   # SQLALCHEMY_DATABASE_URI =os.environ.get('SQLALCHEMY_DATABASE_URI')
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('EMAIL_USER')
    MAIL_PASSWORD = os.environ.get('EMAIL_PASS')