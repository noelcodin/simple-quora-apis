# -*- coding:utf-8 -*-

from common.config import app, HOST, PORT, SSL_CONTEXT, DEBUG
from api.quiz import api

if __name__ == "__main__":
    # https://${HOST}:${PORT}/rest/api/v1
    app.run(HOST, debug=DEBUG, port=PORT, ssl_context=SSL_CONTEXT)