#!/usr/bin/python
# -*- coding:utf-8 -*-

import logging
logging.basicConfig(level=logging.INFO)

from aiohttp import web
import asyncio, os, json, time
from datetime import datetime


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


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init(loop))
    loop.run_forever()


