#! /usr/bin/python
# -*- coding: utf-8 -*-
import os.path
import re
import tornado.auth
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.gen as gen
import tornado.web
import unicodedata
import hashlib
import time
import config
import json
import utils
import redis
import logging

from tornado.options import define, options
 
define("port", default=8888, help="run on the given port", type=int)

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/nearbysearch", GetPoiListHandler),
            (r"/details", GetPoiDetailHandler),
        ]
        settings = dict(
            debug=config.DEBUG,
        )

        tornado.web.Application.__init__(self, handlers, **settings)

        # Have one global connection to the blog DB across all handlers
        # connect to redis
        self.redis_instance = redis.StrictRedis(host = config.REDIS_ADDR, port = config.REDIS_PORT)

class BaseHandler(tornado.web.RequestHandler):
    @property
    def cache(self):
        return self.application.redis_instance
    

class GetPoiListHandler(BaseHandler):
    # /nearbysearch/json?location=39.861099,116.294029&radius=50
    @gen.coroutine
    def get(self):

        checkLoc = self.get_argument("location", None)
        checkRadius = self.get_argument("radius", 50)
        pageToken = self.get_argument("pagetoken", None)

        if not self.cache:
            logging.info("Redis is not connected")
            self.write(json.dumps({"err_code" : 2}))
            self.finish()

        if pageToken is None:
            logging.info("request the first 20 Pois")
            if checkLoc is None:
                logging.info("no location argument")
                self.write(json.dumps({"err_code" : 1}))
                self.finish()

            lat, lng = checkLoc.split(",")

            cache_key = "%s_%s" % (checkLoc, checkRadius)
            if self.cache.get(cache_key):
                logging.info("hit cache key: %s" % cache_key)
                ret_data = '''{"err_code": 0, "results": %s } ''' % (self.cache.get(cache_key))
            else:
                logging.info("unhit cache key: %s, fetch from api." % cache_key)
                http_client = tornado.httpclient.AsyncHTTPClient()
                http_request_uri = "{domain}/nearbysearch/json?location={loc}&radius={r}&{api}".format(
                        domain = config.SERVICE_ADDR,
                        loc = checkLoc,
                        r = checkRadius,
                        api = config.API_PARAMS
                    )
                print http_request_uri
                logging.info("GetPoiList request: %s" % http_request_uri)
                response = yield http_client.fetch(http_request_uri)
                result_list, next_page_token = utils.parse_poi_data(response.body)
                poi_list = utils.filter_poi_infos(result_list)
                utils.calculate_position(poi_list, float(lat), float(lng))
                results = utils.generate_result(poi_list)
                ret_data = '''{"err_code": 0, "results": %s, "next_page_token": "%s"} ''' % (json.dumps(results['results']), next_page_token)
                self.cache.setex(cache_key, 300, json.dumps(results['results']))

        else:
            logging.info("request more Pois by page token parameter")
            pass

        self.write(ret_data)
        self.finish()

class GetPoiDetailHandler(BaseHandler):
    def get(self):
        self.write("Detail Search!")
        self.finish()

def main():
    import sys
    port = int(sys.argv[1].split('=')[1])
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
