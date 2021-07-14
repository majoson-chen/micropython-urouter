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
from . import mimetypes
from .context.session  import Session
from .context.response import Response
from .context.request  import Request
from .router   import uRouter
from .         import consts
from .consts   import __version__
from .         import config


# ======================
request:Request = Request()
response:Response = Response()
session:Session = Session()
# Due to singal-thread, donnot need to care about multithreaded variable derangement
from . import router
router.session = session
router.response = response
router.request = request
# ======================


__all__ = (
    request,
    response,
    session,
    
    consts,
    uRouter,
    mimetypes,
    config,

    __version__,
)
