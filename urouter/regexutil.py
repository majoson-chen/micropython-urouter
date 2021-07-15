#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   regexutil.py
@Time    :   2021/07/10 17:37:02
@Author  :   M-Jay
@Contact :   m-jay-1376@qq.com
'''
# some regex comper and template.

try:
    import ure as re
except:
    import re

# ==============================
MATCH_STRING = "([^\d][^/|.]*)"
MATCH_INT = "(\d*)"
MATCH_FLOAT = "(\d*\.?\d*)"
MATCH_PATH = "(.*)"
VAR_VERI = "<(string|int|float|custom=.*):(\w+)>"  # 匹配URL的规则是否为变量
# ==============================

FIRSTLINE_AGREEMENT = "(GET|POST|HEAD|PUT|DELETE|CONNECT|OPTIONS|TRACE|PATCH) (.*) (.*)"
COMP_HTTP_FIRSTLINE = re.compile(FIRSTLINE_AGREEMENT)