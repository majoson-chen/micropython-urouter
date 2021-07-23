#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   router.py
@Time    :   2021/07/10 17:35:51
@Author  :   M-Jay
@Contact :   m-jay-1376@qq.com
'''

try:
    import usocket as socket
except:
    import socket

from gc import collect
from .config import CONFIG


from .context.session import Session
from .context.response import Response
from .context.request import Request
from .consts import *
from . import logger
from .pool import Poll

# =============================
# These will pass by __init__.py, Don't change them (session = xxx),
# To update these, pleause call xxx.close(), and xxx.init()

# =============================
logger = logger.get("router.main")
collect()

class uRouter():
    # ========vars==========
    _sock: socket.socket
    # _buf: bytearray
    _poll: Poll

    _mode: int
    _root_path: str

    def __init__(
        self,
        host: str = "0.0.0.0",
        port: str = "80",
        root_path: str = "/www",
        mode: int = NORMAL_MODE,
        keep_alive = False,
        backlog: int = 5,
        sock_family: int = socket.AF_INET,
    ):
        """
        Create a router, and then you can add some rule for it.

        :param host: The bound IP, default is "0.0.0.0"
        :param port: The bound port, default is 80
        :param root_path: The storage path of static files, default is "/www"
        :param backlog: appoint the max number of connections at the same time.
        :param mode: appoint the work method, optional `NORMAL_MODE` or `DYNAMIC_MODE`
        :param sock_family: Appoint a sock-family to bind, such as ipv4(socket.AF_INET) or ipv6(socket.AF_INET6). micropython seems that have no ipv6 support, but i provide this param to use in future. defaults to ipv4(AF_INET)
        :type sock_family: Socket.CONSTS, optional
        """
        self.session: Session = Session()
        self.response: Response = Response()
        self.request: Request = Request()

        self._mode = mode

        self._init_sock(host, port, sock_family, backlog)
        self._poll = Poll(
            mode, 
            self._sock, 
            self.request, 
            self.response, 
            self.session,
            keep_alive
        )

        # 格式化路径, 使其规范, root_path 后不能带 /
        if root_path.endswith("/"):
            root_path = root_path[:-1]  # 过滤掉 /
        self._root_path = root_path
        self.response.root_path = root_path

    def _init_sock(
        self,
        host: str,
        port: int,
        family: int,
        backlog: int
    ):
        # init the SOCKET

        self._sock = socket.socket(
            family, socket.SOCK_STREAM)  # SOCK_STREAM (TCP)

        self._sock.setsockopt(
            socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Fastely reuse-tcp

        try:
            self._sock.bind(socket.getaddrinfo(
                host, port)[0][-1])
        except:
            # there may raise a error on esp8266, do not know why.
            self._sock.bind((host, port))

        self._sock.listen(backlog)
        logger.info("Server listening on %s:%s" % (host, port))

    def serve_forever(self):
        """
        Auto-run the web servies, if you want to accept the request in manual by your self, use the function `accept` instead of me.
        When you call me, I'll run all the time after you close the server.
        * This method is only work in NORMAL-MODE
        * This method will block your thread.

        :param timeout: The timeout(ms), if this time is exceeded, we will return. Set a negative number to wait forever, defaults to -1
        :type timeout: int, optional
        """
        assert self._mode != DYNAMIC_MODE, TypeError(
            "This method isn't work in DYNAMIC-MODE")

        logger.info("Start to listen the http requests.")
        while self._sock:  # loop until stop. when stop, _sock will be None
            try:
                self.serve_once()
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.debug("serve error: ", e)
                if CONFIG.debug: 
                    raise e
                    break
                
                

    def serve_once(self, timeout: int = -1) -> bool:
        """
        Wait to accept a request from client in manual, it is disposable, if you need a auto acceptor, pleasue use the function `serve`
        * This method is only work in NORMAL-MODE

        :param timeout: The timeout(ms), if this time is exceeded, we will return. Set a negative number to wait forever, defaults to -1
        :type timeout: int, optional
        :return: If success, return True, failure to False
        """

        self._poll.check(timeout)
        self._poll.process_once()


    # =========
    #  METHODS
    # ↓↓↓↓↓↓↓↓↓
    def close(self):
        """
        Stop the server. If you had been called the func `serve_forever`, it will be return at the last affiar was done.
        """
        self._poll.close()

        self._sock.close()
        self._sock = None




    def route(
        self,
        rule: str,
        methods: iter = (GET, ),
        weight: int = 0
    ):
        """
        Append a rule to the router. For example:
        ```
            @app.route ("/")
            def index ():
                return "<h1>hello world!</h1>"
        ```
        now when you visit the root directory(/), you will see `Hello world`.
        * NOTICE:
            If you append several same rule in a same catching method, we will catch the initial defind.

        :param rule: The url rule.
        :param methods: The method you will catch, you can defind many same rule but in a difference catching-method to achieve different functions, in optional such as `GET`\`POST`\`PUT`\`HEAD`, must be a capital word, defaults to "GET"
        :type methods: iter, optional
        """
        def decorater(func):
            # TODO
            self._poll._rlt.append(rule, func, weight, methods)
            return func
        return decorater


    def websocket(self):
        assert False, NotImplementedError("This is developping") 
        # TODO
