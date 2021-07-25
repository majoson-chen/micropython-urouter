#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   typeutil.py
@Time    :   2021/07/10 17:36:31
@Author  :   M-Jay
@Contact :   m-jay-1376@qq.com

some custom type here.
'''

import collections

ruleitem = collections.namedtuple(
    "rule_item",
    ("weight", "comper", "func", "methods", "url_vars")
)

routetask = collections.namedtuple(
    "route_task",
    ("client", "addr", "http_head", "func", "url_vars")
)

httphead = collections.namedtuple(
    "http_head",
    ("method", "uri", "version")
)

headeritem = collections.namedtuple(
    "header_item",
    ("key", "value")
)