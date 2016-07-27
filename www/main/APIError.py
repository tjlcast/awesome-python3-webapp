#!/usr/bin/python
# -*- coding:utf8 -*-

__author__ = 'tangjialiang'

import json, logging, inspect, functools


class APIError(Exception):
    """
    this base APIError.py which contains error(required), data(optional) and message(optional)
    """
    def __init__(self, error, data='', message=''):
        super(APIError, self).__init__(message)
        self.error = error
        self.data = data
        self.message = message


class APIValueError(APIError):
    """
    Indicate the value has error or invalid. The data specifies the error field of input form
    """
    def __init__(self, field, message=''):
        super(APIValueError, self).__init__('value:invalid', field, message)


class APIResourceError(APIError):
    """
    Indicate the resource was not found. The data specifies the resource name.
    """
    def __init__(self, field, message=''):
        super(APIResourceError, self).__init__('value:notfound', field, message)


class APIPermissionError(APIError):
    """
    Indicate the api has no permission
    """
    def __init__(self, field, message=''):
        super(APIPermissionError, self).__init__('permission:forbidden', 'permission', message)



if __name__ == '__main__':
    pass
