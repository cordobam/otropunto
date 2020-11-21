from flask import Flask

class Config(object):
    SECRET_KEY = 'SUPER SECRET'

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USERNAME= 'cordobam1987@gmail.com'
    MAIL_PASSWORD = 'lingncabewtazqki'
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
