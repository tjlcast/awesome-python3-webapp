#!/usr/bin/python
# -*- coding:utf-8 -*-

__author__ = 'tangjialiang'

import time
import uuid
from orm import StringField
from orm import BooleanField
from orm import FloatField
from orm import Model
from orm import TextField

def next_id():
    return '%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)

class User(Model):
    __table__ = 'users'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    email = StringField(ddl='varchar(50)')
    passwd = StringField(ddl='varchar(50)')
    admin = BooleanField()
    name = StringField(ddl='varchar(50)')
    image = StringField(ddl='varchar(50)')
    created_at = FloatField(default=time.time)


class Blog(Model):
    __table__ = 'blog'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    user_id = StringField(ddl='varchar(50)')
    user_name = StringField(ddl='varchar(50)')
    user_image = StringField(ddl='varchar(50)')
    name = StringField(ddl='varchar(50)')
    summary = StringField(ddl='varchar(50)')
    content = TextField()
    created_at = FloatField(default=time.time)


class Comment(Model):
    __table__ = 'comment'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    blog_id = StringField(ddl='varchar(50)')
    user_id = StringField(ddl='varchar(50)')
    user_name = StringField(ddl='varchar(50)')
    user_image = StringField(ddl='varchar(50)')
    content = TextField()
    created_at = FloatField(default=time.time)


# ====================================  test ##########################################################################
import orm
import sys
import asyncio
def test_connect_db_connect(loop):
    yield from orm.create_pool(loop)
    u = User(name='Test', email='test@example.com', passwd='12345678', image='about;blank')
    yield from u.save()


if __name__ == '__main__':
    print('begin')
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait([test_connect_db_connect(loop)]))
    loop.close()

    if loop.is_closed():
        sys.exit(0)
