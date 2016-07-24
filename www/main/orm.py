#!/usr/bin/python
# -*- coding:utf-8 -*-

import logging
logging.basicConfig(level=logging.INFO)
import asyncio, os, json, time
import aiomysql
from datetime import datetime


__author__ = 'tangjialiang'


def create_args_string(num):
    """
    :func 依据输入的num生成相应数量sql中的'?'
    :param num:
    :return:
    """
    L = []
    if isinstance(num, int)==False:
        raise Exception('num is not int, num : %s' % num.__class__)
    for n in range(num):
        L.append('?')
    return ', '.join(L)


class Field(object):
    def __init__(self, name, column_type, primary_key, default):
        self.name = name
        self.column_type = column_type
        self.priamry_key = primary_key
        self.default = default
    def __str__(self):
        return '<%s, %s:%s>' % (self.__class__.__name__, self.column_type, self.name)


class StringField(Field):
    def __init__(self, name=None, primary_key=False, default=None, ddl='varchar(100)'):
        super(StringField, self).__init__(name, primary_key=primary_key, default=default, column_type=ddl)


class IntegerField(Field):
    def __init__(self, name=None, primary_key=False, default=0, ddl='varchar(100)'):
        super(IntegerField, self).__init__(name, ddl, primary_key=primary_key, default=default)


class BooleanField(Field):
    def __init__(self, name=None, primary_key=False, default=False):
        super(BooleanField, self).__init__(name, 'boolean', primary_key, default)


class FloatField(Field):
    def __init__(self, name=None, primary_key=False, default=0.0):
        super(FloatField, self).__init__(name, 'real', primary_key=primary_key, default=default)


class TextField(Field): 
    def __init__(self, name=None, primary_key=False, default=None):
        super(TextField, self).__init__(name, 'text', primary_key=primary_key, default=default)


class ModelMetaclass(type):
    def __new__(cls, name, bases, attrs):
        if name == 'Model':
            return type.__new__(cls, name, bases, attrs)
        mappings = dict()
        tableName = attrs.get('__table__', None) or name
        fields = []
        primaryKey = None
        for k, v in attrs.items():
            if isinstance(v, Field):
                logging.info('  found mapping: %s ==> %s' % (k, v))
                mappings[k] = v
                if v.primary_Key:
                    # 找到主键
                    if primaryKey:
                        raise RuntimeError('Duplicate primary key for field: %s' % k)
                    primaryKey = k
                else:
                    fields.append(k)
        if not primaryKey:
            raise RuntimeError('Primary key not found.')
        for k in mappings.keys():
            attrs.pop(k)
        escaped_fields = list(map(lambda f: '`%s`' % f, fields))
        attrs['__table__'] = tableName
        attrs['__mappings__'] = mappings
        attrs['__table__'] = name
        attrs['__primary_key__'] = primaryKey
        attrs['__fields__'] = fields
        attrs['__select__'] = 'select `%s`, %s from `%s`' % (primaryKey, ', '.join(escaped_fields), tableName)
        attrs['__insert__'] = 'insert into `%s` (%s, `%s`) values (%s)' % (tableName, ', '.join(escaped_fields), primaryKey, create_args_string(len(escaped_fields) + 1))
        attrs['__update__'] = 'update `%s` set %s where `%s`=?' % (
        tableName, ', '.join(map(lambda f: '`%s`=?' % (mappings.get(f).name or f), fields)), primaryKey)
        attrs['__delete__'] = 'delete from `%s` where `%s`=?' % (tableName, primaryKey)
        return type.__new__(cls, name, bases, attrs)


class Model(dict, metaclass=ModelMetaclass):
    def __init__(self, **kw):
        super(Model, self).__init__(**kw)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'model' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        self[key] = value

    def getValue(self, key):
        return getattr(self, key, None)

    def getValueOrDefault(self, key):
        value = getattr(self, key, None)
        if value is None:
            field = self.__mappings__[key]
            if field.default is not None:
                value = field.default if callable(field.default) else field.default
                logging.debug('using default value for %s: %s' % (key, str(value)))

    @asyncio.coroutine
    def save(self):
        args = list(map(self.getValueOrDefault, self.__fields__))
        args.append(self.getValueOrDefault(self.__primary_key__))
        rows = yield from execute(self.__insert__, args)
        if rows != 1:
            logging.info('save: rows is not 1!(row=%s)' % rows)

    @classmethod
    @asyncio.coroutine
    def find(cls, pk):
        """
        :doc find object by primary key.:
        """
        rs = yield from select('%s where `%s`=?' % (cls.__select__, cls.__primary_key__), [pk], 1)
        if len(rs) == 0:
            return None
        return cls(**rs[0])

    @classmethod
    @asyncio.coroutine
    def findAll(cls, where=None, args=None, **kw):
        'find all cases by where clause'
        sql = [cls.__select__]
        if where:
            sql.append('where')
            sql.append(where)
        if args is None:
            args = []
        orderBy = kw.get('orderBy', None)
        if orderBy:
            sql.append('order by')
            sql.append(orderBy)
        limit = kw.get('limit', None)
        if limit is not None:
            sql.append('limit')
            if isinstance(limit, int):
                pass
            elif isinstance(limit, tuple) and len(limit) == 2:
                pass
            else:
                raise ValueError('Invaild limit value: %s' % str(limit))
        rs = yield from select(''.join(sql), args)
        return [cls(**r) for r in rs ] ##给该类实例！！


    @classmethod
    @asyncio.coroutine
    def findNumber(cls, selectField, where=None, args=None):
        'find number by select and number'
        sql = ['select %s _num_ from `%s`' % (selectField, cls.__table__)]
        if where:
            sql.append('where')
            sql.append(where)
        rs = yield from select(' '.join(sql), args, 1)
        if len(rs) == 0:
            return None
        return rs[0]['__num__']

    @asyncio.coroutine
    def update(self):
        args = list(map(self.getValue, self.__field__))
        args.append(self.getValue(self.__primary_key__))
        rows = yield from execute(self.__update, args)
        if rows != 1:
            logging.warning('failed to update to primary key: affected rows: %s' % str(rows))

    @asyncio.coroutine
    def remove(self):
        args = [self.getValue(self.__primary_key__)]
        rows = yield from execute(self.__delete__, args)
        if rows != 1:
            logging.warning('failed to remove by primary key: affected rows: %s' % str(rows))

#=========================================about database pool ==========================================================

# 数据库连接池
@asyncio.coroutine
def create_pool(loop, **kw):
    logging.info('create database connection pool...')
    global __pool
    __pool = yield from aiomysql.create_pool(
        host = kw.get('host', 'locahost'),
        port = kw.get('port', 3306),
        user = kw.get('www-data'),
        password = kw.get('destination'),
        db = kw.get('awesome'),
        charset = kw.get('charset', 'utf8'),
        autocommit = kw.get('maxsize', True),
        maxsize = kw.get('maxsize', 10),
        minsize = kw.get('minszie', 10),
        loop = loop
    )

#数据库的select
@asyncio.coroutine
def select(sql, args, size=None):
    logging.info('select: sql: {sql} args: {args}'.format(sql=sql, args=args))
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

#数据库的execute
@asyncio.coroutine
def execute(sql, args):
    logging.info('execute: sql: {sql} args: {args}'.format(sql=sql, args=args))
    global __pool
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
    testStr = create_args_string(3)
    create_pool()

    pass