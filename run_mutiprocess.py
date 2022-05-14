# -*- coding:utf-8 -*-

from gevent import monkey
from gevent.pywsgi import WSGIServer
from multiprocessing import cpu_count, Process

from common.config import app, HOST, PORT, KEYFILE, CERTFILE
from api.quiz import api

monkey.patch_all()


def run(MULTI_PROCESS):
    if not MULTI_PROCESS:
        WSGIServer((HOST, PORT), app, keyfile=KEYFILE, certfile=CERTFILE).serve_forever()
    else:
        mulserver = WSGIServer((HOST, PORT), app, keyfile=KEYFILE, certfile=CERTFILE)
        mulserver.start()

        def server_forever():
            mulserver.start_accepting()
            mulserver._stop_event.wait()

        for i in range(cpu_count()):
            p = Process(target=server_forever)
            p.start()

if __name__ == "__main__":
    # single thread
    #run(False)
    # multi threads
    run(True)