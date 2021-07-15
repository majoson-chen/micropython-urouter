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
from .ruleutil import RuleTree
from .queue import Queue
from .config import config
from .context.session import Session
from .context.response import Response
from .context.request import Request
from .consts import *
from . import logger

# =============================
# These will pass by __init__.py, Don't change them (session = xxx),
# To update these, pleause call xxx.close(), and xxx.init()
session: Session = None
response: Response = None
request: Request = None
# =============================
logger = logger.get("router.main")


class uRouter():
    # ========vars==========
    _sock: socket.socket
    _queue: Queue
    _buf: bytearray
    _rlt: RuleTree

    _mode: int
    _root_path: str
    _backlog: int
    _listening: bool = False

    def __init__(
        self,
        host: str = "0.0.0.0",
        port: str = "80",
        root_path: str = "/www",
        backlog: int = 5,
        mode: int = NORMAL_MODE,
        sock_family: int = socket.AF_INET
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
        self._buf = bytearray(64)
        self._rlt = RuleTree()

        # Create a everlasting mem area,
        # Avoid runtime memory allocation.

        self._mode = mode
        if mode == DYNAMIC_MODE:
            self._queue = Queue()
            self._sock.setsockopt(socket.SOL_SOCKET, 20, self._accept_to_queue)

        self._backlog = backlog
        self._init_sock(host, port, sock_family)

        # 格式化路径, 使其规范, root_path 后不能带 /
        if root_path.endswith("/"):
            root_path = root_path[:-1]  # 过滤掉 /
        self._root_path = root_path
        response.root_path = root_path

    def _init_sock(
        self,
        host: str,
        port: int,
        family: int
    ):
        # init the SOCKET

        self._sock = socket.socket(
            family, socket.SOCK_STREAM)  # SOCK_STREAM (TCP)

        self._sock.setsockopt(
            socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Fastely reuse-tcp

        self._sock.bind(socket.getaddrinfo(
            host, port)[0][-1])

        self._sock.listen(self._backlog)
        logger.info("Server listening on %s:%s" % (host, port))

    def _accept_once(self, client: socket.socket = None):
        """
        Accept one request.
        If time out, it will raise a time-out Error.

        :param timeout: When the system call it(call-back), it will be a socket instance, when the func `serve_once` call it, it will be a timeout param.
        """
        client, addr = self._sock.accept()

        try:
            self._process_req(client, addr)
        except Exception as e:
            client.close()
            logger.debug("process req failed.")
            if config.logger_level == DEBUG: raise e

        collect()

    def _process_req(
        self,
        client: socket.socket,
        addr: tuple
    ):
        global request, response, session
        logger.debug("process req.")
        client.settimeout(config.request_timeout)
        try:
            # create a new context, do not change the context obj's pointer,
            # just modify on them self.
            request.init(client, addr)
            response.init(client)
            session.init(request, response)
        except Exception as e:
            logger.error("faild to create new context: ", e)
            if config.logger_level == DEBUG:
                raise e
            return

        rlt = None
        try:
            # start to process the request.
            rlt = self._rlt.match(request.url, request.method)
        except Exception as e:
            if config.logger_level == DEBUG: raise e
            logger.error("An error occurred during route matching: ", e)

        if rlt:
            # rule hited
            _, func, kwargs = rlt
            logger.debug("rule hited: ", func)
            try:
                rlt = func(**kwargs)

                if not response._responsed:
                    # 还未响应过
                    if rlt != None:
                        # 有内容
                        response.make_response(rlt)
                    else:
                        # 无内容
                        response.abort()
                        response.make_response("The processing function\
did not return any data")
                # else:
                    # 响应过了, 不执行任何操作

            except Exception as e:
                # 处理错误, 500 状态码安排上
                logger.error("router function error happended: ", e)
                response.abort()
                if config.logger_level == DEBUG: raise e
        else:
            # rule not hited, try to send local file.
            logger.debug("rule not hited, try to send local-file")
            try:
                response.send_file(request.url)
                # 已经发送文件 | 发送404
            except Exception as e:
                logger.error("failed to send local file: ", e)
                # 处理错误, 500 状态码安排上
                response.abort()
                if config.logger_level == DEBUG:
                    raise e
        

        # After processing, flush the data-stream and close the connection.
        while True:
            # flush
            if client.readinto(self._buf):
                continue
            else:
                # read-len == 0, flush over.
                break
        response._close()
        logger.info(response.statu_code, " - ", addr, " - ", request.url)
 
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

        while self._sock:  # loop until stop. when stop, _sock will be None
            try:
                self.serve_once()
            except KeyboardInterrupt:
                break
            except Exception as e:
                if config.logger_level == DEBUG: raise e
                logger.debug("serve error: ", e)

    def serve_once(self, timeout: int = None) -> bool:
        """
        Wait to accept a request from client in manual, it is disposable, if you need a auto acceptor, pleasue use the function `serve`
        * This method is only work in NORMAL-MODE

        :param timeout: The timeout(ms), if this time is exceeded, we will return. Set a negative number to wait forever, defaults to -1
        :type timeout: int, optional
        :return: If success, return True, failure to False
        """
        assert self._mode != DYNAMIC_MODE, TypeError(
            "This method isn't work in DYNAMIC-MODE")

        self._sock.settimeout(timeout)

        try:
            self._accept_once()
            return True
        except KeyboardInterrupt as e:
            raise e
        except OSError:
            # TIMEOUT
            pass
        except Exception as e:
            if config.logger_level == DEBUG: raise e
            return False

    # ↑↑↑↑↑↑↑↑↑↑↑↑
    # NORMAL-MODE
    # ============

    # ============
    # DYNAMIC-MODE
    # ↓↓↓↓↓↓↓↓↓↓↓↓
    def _accept_to_queue(self, client: socket.socket):
        """
        When a new sock request comes in, this will be called.
        """

        # TODO
        # 匹配路由后添加到队列

    def check_queue(self) -> int:
        """
        When the cpu has free time, you can call this method to handler one request.
        * This method is only available on `DYNAMIC-MODE`.
        """
        assert self._mode == NORMAL_MODE, TypeError(
            "This method isn't work in NORMAL-MODE")

        # TODO - 使用 select 检查

    def handle_queue(self, amount: int):
        """
        Handle the requests in the queue
        * This method is only available on `DYNAMIC-MODE`.

        :param amount: int, Appoint the amount you will handle
        """
        assert self._mode == NORMAL_MODE, TypeError(
            "This method isn't work in NORMAL-MODE")

    # =========
    #  METHODS
    # ↓↓↓↓↓↓↓↓↓
    def close(self):
        """
        Stop the server. If you had been called the func `serve_forever`, it will be return at the last affiar was done.
        """
        self._sock.close()
        self._sock = None

    def route(
        self,
        rule: str,
        methods: iter = (GET, ),
        weight: int = 1000
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
            self._rlt.append(rule, func, weight, methods)
            return func
        return decorater

    def websocket(self):
        assert False, "This is developping"
        # TODO
