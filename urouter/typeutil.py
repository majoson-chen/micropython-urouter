#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   typeutil.py
@Time    :   2021/07/10 17:36:31
@Author  :   M-Jay
@Contact :   m-jay-1376@qq.com
'''
# some custom type here.

try:
    import ucollections as collections
except:
    import collections

ruleitem = collections.namedtuple(
    "ruleitem",
    ("rule", "func", "methods", "url_vars")
)
ruletask = collections.namedtuple(
    "ruletask",
    ("weight", "task")
)

headeritem = collections.namedtuple(
    "header_item",
    ("key", "value")
)