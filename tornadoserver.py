#!/usr/bin/env python
import os
import tornado.httpserver
import tornado.ioloop
import tornado.wsgi
import sys
from django_wsgi import application

def main():
    container = tornado.wsgi.WSGIContainer(application)
    http_server = tornado.httpserver.HTTPServer(container)
    http_server.listen(1770)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
