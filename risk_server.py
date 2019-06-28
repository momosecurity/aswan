# coding=utf8
"""A http server which offers two uri: query and report"""
from gevent import monkey

monkey.patch_all()  # noqa

import json
from cgi import FieldStorage
from gevent.pywsgi import WSGIServer
from server import query_handler, report_handler
from config import RISK_SERVER_HOST, RISK_SERVER_PORT

URL_2_HANDLERS = {
    "/query/": query_handler,
    "/report/": report_handler,
}


def __parse_post_body(environ, ignore_get=False):
    post_data = {}

    # accept post json
    if environ["CONTENT_TYPE"].strip(';') == "application/json" and environ["REQUEST_METHOD"] == "POST":
        storage = environ['wsgi.input'].read()
        if storage:
            return json.loads(storage)

    storage = FieldStorage(environ['wsgi.input'], environ=environ, keep_blank_values=True)

    # accept get querystring
    if not ignore_get:
        for k in storage.keys():
            post_data[k] = storage.getvalue(k)

    return post_data


def application(environ, start_response):
    if environ['PATH_INFO'] not in URL_2_HANDLERS:
        response = json.dumps({"ec": 0, "error": "invalid uri"})
        start_response('200 OK', [('Content-Type', 'application/json')])
        return [response]

    handler = URL_2_HANDLERS[environ['PATH_INFO']]
    post_data = __parse_post_body(environ, ignore_get=False)
    response = handler(post_data)
    start_response('200 OK', [('Content-Type', 'application/json')])
    return [str(response).encode()]


def serve_forever():
    WSGIServer((RISK_SERVER_HOST, RISK_SERVER_PORT), application).serve_forever()


if __name__ == "__main__":
    serve_forever()
