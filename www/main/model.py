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
    __table__ = 'user'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    email = StringField(ddl='varchar(50)')
    passwd = StringField()
    admin = BooleanField()
    name = StringField()
    image = StringField()
    created_at = FloatField()


class Blog(Model):
    __table__ = 'blog'

    id = StringField()
    user_id = StringField()
    user_name = StringField()
    user_image = StringField()
    name = StringField()
    summary = StringField()
    content = TextField()
    created_at = FloatField(default=time.time)


class Comment(Model):
    __table__ = 'comment'

    id = StringField()
    blog_id = StringField()
    user_id = StringField()
    user_name = StringField()
    user_image = StringField()
    content = TextField()
    created_at = FloatField(default=time.time)


if __name__ == '__main__':
    pass
