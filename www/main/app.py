#!/usr/bin/python
# -*- coding:utf-8 -*-

import logging
logging.basicConfig(level=logging.INFO)

from aiohttp import web
import asyncio, os, json, time
import functools
from orm import create_pool
import jinja2
from datetime import datetime

#============================================about middleware===========================================================

@asyncio.coroutine
def logger_factory(app, handler):
    @asyncio.coroutine
    def logger(request):
        # 记录日志
        logging.info('Request: %s %s' % (request.method, request.path))
        # 继续处理请求
        return (yield from handler(request))
    return logger

@asyncio.coroutine
def response_factory(app, handle):
    @asyncio.coroutine
    def response(request):
        # 结果
        r = yield from handle(request)
        if isinstance(r, web.StreamResponse):
            return r
        if isinstance(r, bytes):
            resp = web.Response(body=r)
            resp.content_type = 'application/octet-stream'
            return resp
        if isinstance(r, str):
            resp = web.Response(body=r.encode('utf-8'))
            resp.content_type = 'text/html;charset=utf-8'
            return resp
        if isinstance(r, dict):
            pass


#==============================================app======================================================================



@asyncio.coroutine
def index(request):
    return web.Response(body=b"<body>Hello world</body>")


@asyncio.coroutine
def init(loop):
    app = web.Application(loop=loop)
    app.router.add_route('GET', '/', index)
    srv = yield from loop.create_server(app.make_handler(), '127.0.0.1', 8086)
    logging.info('server started at http://127.0.0.1:8086.....')
    return srv


def get_required_kw_args(fn):
    pass


def get_named_kw_args(fn):
    pass


def has_named_kw_args(fn):
    pass


def has_var_kw_arg(fn):
    pass


def has_request_arg(fn):
    pass


class RequestHandle(object):

    def __init__(self, app, fn):
        self._app = app
        self._func = fn


    @asyncio.coroutine
    def __call__(self, request):
        r = yield from self._func(**kw)
        return r

def add_route(app, fn):
    """
    :func 对url处理函数进行一步封装(RRequestHandle)，再把封装的url处理函数添加到app的router中:
    :param app:
    :param fn:
    :return:
    """
    method = getattr(fn, '__methode__', None)
    path = getattr(fn, '__path__', None)

    if method is None or path is None:
        raise ValueError('@get or @post is not defined in %s.' % str(fn))
    if not asyncio.iscoroutine(fn) and not inspect.isgeneratorfunction(fn):
        fn = asyncio.coroutine(fn)
    logging.info('add route %s %s => %s(%s)' % (method, path, fn.__name__, ','.join(inspect.signature(fn).parameters.keys())))
    app.router.add_route(method, path, RequestHandle(app, fn))


def add_routes(app, module_name):
    n = module_name.rfind('.')
    if n == -1:
        mod = __import__(module_name, globals(), locals())
    else:
        name = module_name[n+1:]
        mod = getattr(__import__(module_name[:n], globals(), locals(), [name]), name)

    for attr in dir(mod):
        if attr.startswith('_'):
            continue
        fn = getattr(mod, attr)
        if callable(fn):
            method = getattr(fn, '__method__', None)
            path = getattr(fn, '__path__', None)
            if method and path:
                add_route(app, fn)
    pass


#=========================================ABOUT GET AND POST============================================================


def get(path):
    def decorator(func):
        # 在该层内对func进行重新构建：wraps
        @functools.wraps(func)
        def wrapper(*args, **kw):
            return func(*args, **kw)
        wrapper.__method__ = 'GET'
        wrapper.__route__ = path
        return wrapper
    return decorator


def post(path):
    def decorator(func):
        # 在该层内对func进行重新构建：wraps
        @functools.wraps(func)
        def wrapper(*args, **kw):
            return func(*args, **kw)
        wrapper.__method__ = 'POST'
        wrapper.__route__ = path
        return wrapper
    return decorator


#=============================================start====================================================================

loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init(loop))
    loop.run_forever()


