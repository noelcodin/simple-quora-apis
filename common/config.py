# -*- coding:utf-8 -*-

import datetime
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
import logging
from settings import rootPath

# db connection info
mysqlConn='mysql+pymysql://root:root@localhost/quiz_db'

api_prefix = "/rest/api/v1"

# web config
HOST = "127.0.0.1"
PORT = 8100
SSL_CONTEXT = 'adhoc'
DEBUG = True

# jwt secret
SECRET_KEY = "987QuizBuilder012"

# Hashids salt
SALT = "987QuizBuilderSalt012"

# ssl certificates
KEYFILE = 'key.pem',
CERTFILE = 'cert.pem'


# return an app with db connection and logger
def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = mysqlConn
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logdir = rootPath + "\logs\\"
    if not os.path.exists(logdir):
        os.makedirs(logdir)
    logpath = logdir + str(datetime.date.today()) + ".log"
    file_handler = logging.FileHandler(logpath, encoding='UTF-8')
    file_handler.setFormatter(formatter)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    return app

app = create_app()
db = SQLAlchemy(app)
api = Api(app)


