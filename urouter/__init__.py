# Copyright 2021 github@Li-Lian1069 m-jay.cn
# GNU LESSER GENERAL PUBLIC LICENSE
#                        Version 3, 29 June 2007
#  Copyright (C) 2007 Free Software Foundation, Inc. <https://fsf.org/>
#  Everyone is permitted to copy and distribute verbatim copies
#  of this license document, but changing it is not allowed.
# @author m-jay
# @E-mail m-jay-1376@qq.com
"""
A lightweight HTTP request routing processing support library based on micropython.  
 The previous name was [micro-route](https://github.com/Li-Lian1069/micro_route)
"""

from .consts   import *
from .router   import uRouter
from .config   import CONFIG
from .mimetypes import get as get_mime_type

__version__ = 'v0.1.1 alpha'

__all__ = (
    uRouter, 
    CONFIG,

    __version__,

    GET,
    POST,
    HEAD,
    PUT,
    OPINOS,
    DELETE,
    TRACE,
    CONNECT,
    NORMAL_MODE,
    DYNAMIC_MODE,
    
    get_mime_type
)