#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   __init__.py
@Time    :   2021/07/23 16:21:55
@Author  :   M-Jay
@Contact :   m-jay-1376@qq.com

Manage connections and http requests.
'''

from gc import collect
import socket
import select
from ..config import CONFIG
from ..consts import DYNAMIC_MODE, placeholder_func
from .queue import Queue
from ..ruleutil import RuleTree

from ..regexutil import comp_head
from ..typeutil import httphead, routetask

from ..context.request import Request
from ..context.response import Response
from ..context.session import Session

from .. import logger
logger = logger.get("uRouter.poll")


class Poll:
    _host: socket.socket
    _poll: select.poll
    _conns: list
    _queue: Queue
    _rlt: RuleTree
    # _conns = [
    #     "socket clients"
    #     (client1, addr),
    #     (client2, addr)
    # ]

    _mode: int
    max: int

    request: Request
    response: Response
    session: Session

    def __init__(
        self,
        mode: int,
        host: socket.socket,
        request,
        response,
        session,
        keep_alive
    ):

        self.max = CONFIG.max_connections
        # Make sure that there is always a place available

        self._rlt = RuleTree()
        self._mode = mode
        self._conns = []
        self._host = host
        self._poll = select.poll()
        if not hasattr(self._poll, "ipoll"):
            self._poll.ipoll = self._poll.poll  # for pc debug.

        self._poll.register(host, select.POLLIN | select.POLLERR)
        self._queue = Queue()

        if mode == DYNAMIC_MODE:
            host.setblocking(False)

        self.request = request
        self.response = response
        self.session = session
        self._keep_alv = keep_alive

    def close(self):
        for client, _ in self._conns:
            self._poll.unregister(client)
            try:
                client.close()
            except:
                ...

        self._poll.unregister(self._host)

        self._queue._heap.clear()

    def _find_addr(self, client: socket.socket):
        """
        Find the addr of the client in conns

        :return: if not found, return None.
        """
        n = 0
        while n < len(self._conns):
            client_, addr = self._conns[n]
            if client_ == client:
                return addr
            n += 1
        return None  # Not found.

    def _append_conn(self, client, addr):
        if (client, addr) in self._conns:
            # exist already.
            return
        else:
            client.settimeout(CONFIG.request_timeout)
            self._conns.insert(0, (client, addr))
            self._poll.register(client, select.POLLIN | select.POLLERR)
            return

    def _pop_conn(self, client: socket.socket = None):
        """
        Pop the connetion from _conns.
        * if pass nothing, it will pop the earliest conn.
        if exist, pop it , if not, just close it.
        """
        if len(self._conns) == 0:
            self._poll.unregister(client)
        elif client:
            # pop the appointed conn.
            for idx, (sock, _) in enumerate(self._conns):
                if sock == client:
                    self._conns.pop(idx)
                    break
        else:
            # pop the earlist conn.
            client, _ = self._conns.pop()

        self._poll.unregister(client)
        try:
            client.close()
        except:
            ...

    def _append_to_queue(self, client: socket.socket, addr: tuple):
        """
        Read the http-head and try to match the handler, 
        finally append it to the queue.

        * This function will not try to catch exceptions. 
        """
        client.settimeout(CONFIG.request_timeout)
        try:
            line = client.readline().decode().strip()
        except OSError as e:
            # timeout
            logger.debug("Http head read timeout.")
            self._pop_conn(client)
            return None
        head: httphead = comp_head(line)
        if not head:
            # head not matched.
            self._pop_conn(client)
            logger.debug("http head-line do not matched.")
            return None

        # head matched.
        # handler = self._rlt.match(head.uri, head.method)

        (weight, func, kwargs) = self._rlt.match(head.uri, head.method)

        self._queue.push(
            weight, routetask(client, addr, head, func, kwargs)
        )
        # ("weight", "client", "addr", "http_head", "func", "url_vars")

    def check(self, timeout: int) -> int:
        """
        Check the new request or new connetcions, and append them into Queue.

        :return: the quantity of waiting tasks.
        """

        # if self._mode == NORMAL_MODE:
        #     clients = self._poll.ipoll(timeout)
        # elif self._mode == DYNAMIC_MODE:
        #     clients = self._poll.ipoll(0)
        if self._queue._heap:
            # task waiting
            # return len(self._queue._heap)
            logger.debug("task exist, skip check.")
            return len(self._queue._heap)

        # have no wating tasks, try to accept any.

        logger.debug("check the new requests, timeout: ", timeout)

        clients = (
            self._poll.poll(0)  # non-block
            if
            self._mode == DYNAMIC_MODE
            else
            # self._poll.poll(timeout)
            self._poll.poll(timeout)
        )

        if not clients:
            return 0

        client: socket.socket
        for client, event in clients:
            if client == self._host and event == select.POLLIN:  # new connect.
                while len(self._conns) >= self.max:
                    # if connections fulfill
                    # pop the earliest conn
                    self._pop_conn()
                    logger.debug("Conns fulfill, close one.")

                # append new to conns.
                try:
                    client, addr = self._host.accept()
                    # self._conns.insert(0, (client, addr)) # Append to conns.
                    # self._poll.register(client)
                    self._append_to_queue(client, addr)
                    logger.debug("New conn: ", addr)
                    continue
                except OSError as e:
                    if e.args == (23,):
                        # The number of connections exceeds the system limit
                        # reduce the max quantity.
                        self.max == len(self._conns)
                        logger.warn(
                            "The maximum number of connections you set exceeds the system limit. The max quantity is: ",
                            len(self._conns)
                        )
                        continue
                    else:
                        logger.warn(
                            "Unknown error when accept a new connection: ", e)
                        # if CONFIG.debug: raise e  # debug
            else:  # Existing connections.
                if event == select.POLLIN:  # New request.
                    addr = self._find_addr(client)
                    # try:
                    self._append_to_queue(client, addr)
                    continue
                elif event == select.POLLERR:  # ERR happend, close it.
                    self._pop_conn(client)
                    logger.warn("A socket obj error, close it.")

        collect()
        return len(self._queue._heap)

    def process_once(self):
        """
        * In nromal-mode, it will wait a request and handle it befor timeout.
        * In dynamic-mode, it will check whether there is a new request, \
        if there is, it will process it, if not, it will return directly(non-blocking).
        """
        # task: routetask = self._queue.pop()
        # routetask: ("weight", "client", "addr", "http_head", "func", "url_vars")

        client: socket.socket
        head: httphead

        task: routetask = self._queue.pop_task()

        if task == None:
            # have no task.
            logger.debug("have no new request.")
            return
        else:
            client, addr, head, func, kwargs = task

        request = self.request
        response = self.response
        session = self.session

        request.init(client, addr, head)
        response.init(client)
        session.init(request, response)

        if self._keep_alv:
            if 'keep-alive' in request.headers.get("Connection", ""):
                keep = True
                response.headers["Connection"] = "keep-alive"
            else:
                keep = False
                response.headers["Connection"] = "close"
        else:
            keep = False
            response.headers["Connection"] = "close"

        if func != placeholder_func:
            # rule hited
            # logger.debug("rule hited: ", func)
            try:
                rlt = func(**kwargs)
                # After processing, flush the data-stream and close the connection.
                response._flush()

                if response._stream_mode:
                    if not response._stream_finish:
                        response.finish_stream()
                elif not response._responsed:
                    # 还未响应过
                    if rlt != None:
                        # 有内容
                        response.make_response(rlt)
                    else:
                        # 无内容
                        response.statu_code = 500
                        response.make_response(
                            "The processing function did not return any data")
            except OSError:
                # Timeout
                # skip this request
                logger.debug("process timeout: ", request.url)
                self._pop_conn(client)
                return
            except Exception as e:
                # 处理错误, 500 状态码安排上
                logger.error("router function error happended: ", e)
                response.abort()
                if CONFIG.debug:
                    raise e
        else:
            # rule not hited, try to send local file.
            # logger.debug("rule not hited, try to send local-file")
            try:
                # After processing, flush the data-stream and close the connection.
                response._flush()
                response.send_file(request.url)
                # 已经发送文件 | 发送 404
            except OSError:
                # Timeout
                # skip this request
                logger.debug("process timeout: ", request.url)
                self._pop_conn(client)
                return
            except Exception as e:
                logger.error("failed to send local file: ", e)
                # 处理错误, 500 状态码安排上
                response.abort()
                if CONFIG.debug:
                    raise e

        if keep:
            # keep-alive
            # client.setblocking(False)
            self._append_conn(client, addr)
            # logger.debug("Responsed, keep alive.")
        else:
            # close
            self._pop_conn(client)
            # logger.debug("Responsed, close it.")

        logger.info(response.statu_code, ": ", addr, " > ", request.url)
        collect()
