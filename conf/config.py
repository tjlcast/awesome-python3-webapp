#!/usr/bin/python
# -*- coding: utf-8 -*-


import config_default

__author__ = 'tanjialiang'

class Dict(dict):
    def __init__(self, names=(), values=(), **kw):
        super(Dict, self).__init__(**kw)
        for k, v in zip(names, values):
            self[k] = v

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Dict' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        self[key] = value


def merge(defualt_config, override_config):
    r = {}
    for k, v in defualt_config:
        if k in override_config:
            if isinstance(v, dict):
                r[k] = merge(v, override_config[k])
            else:
                r[k] = override_config[k]
        else:
            r[k] = v
    return r


def toDict(d):
    D = Dict()
    if isinstance(d, dict)==False:
        raise Exception('toDict: %s is not dict' % d.__class__)
    for k, v in d.items():
        D.k = v if isinstance(v, dict) else toDict(v)
    return D


configs = config_default.configs

try:
    import config_override
    merge(configs, config_override.configs)
except ImportError:
    pass

if __name__ == '__main__':
    pass