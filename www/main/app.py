#!/usr/bin/python
# -*- coding:utf-8 -*-

import logging
import aiomysql
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


# 数据库连接池
@asyncio.coroutine
def create_pool(loop, **kw):
    logging.info('create database connection pool...')
    global __pool
    __pool = yield from aiomysql.create_pool(
        host = kw.get('host', 'locahost'),
        port = kw.get('port', 3306),
        user = kw.get('user'),
        password = kw.get('password'),
        db = kw.get('db'),
        charset = kw.get('charset', 'utf8'),
        autocommit = kw.get('maxsize', True),
        maxsize = kw.get('maxsize', 10),
        minsize = kw.get('minszie', 10),
        loop = loop
    )

#数据库的sql
@asyncio.coroutine
def select(sql, args, size=None):
    log(sql, args)
    global __pool
    with (yield from __pool) as conn:
        cur = yield from conn.cursor()
        yield from cur.execute(sql.replace('?', '%s'), args)
        if size:
            rs = yield from cur.fetchmany(size)
        else:
            rs = yield from cur.fetchall()
        yield from cur.close()
        logging.info('rows returned: %s' % len(rs))
        return rs

#数据库的执行
@asyncio.coroutine
def execute(sql, args):
    log(sql)
    with (yield from __pool) as conn:
        try:
            cur = yield from conn.cursor()
            yield from cur.execute(sql.replace('?', '%s'), args)
            affected = cur.rowcount
            yield from cur.close()
        except BaseException as e:
            raise
        return affected



if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init(loop))
    loop.run_forever()


