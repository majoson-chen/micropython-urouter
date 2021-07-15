#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   logger.py
@Time    :   2021/07/10 17:36:04
@Author  :   M-Jay
@Contact :   m-jay-1376@qq.com
'''
# the logger mg.

import ulogger
from .config import CONFIG

handler = ulogger.Handler(CONFIG.logger_level)

def get(name: str) -> ulogger.Logger:
    return ulogger.Logger(
        name=name,
        handlers=(handler, )
    )
