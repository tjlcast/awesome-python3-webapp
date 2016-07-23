#!/usr/bin/python
#-*- coding:utf-8 -*-

__author__ = 'tangjialiang'

from model import User
from app import get


@get('/')
def index(request):
    users = yield from User.findAll()
    return {
        '__template__' : 'test.html',
        'user' : users ,
    }

if __name__ == '__main__':
    pass