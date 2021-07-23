#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   request.py
@Time    :   2021/07/23 17:06:57
@Author  :   M-Jay
@Contact :   m-jay-1376@qq.com

Used to obtain connection information.
'''

import socket

from ..consts import *
from ..util import *
from ..config import CONFIG
from ..typeutil import headeritem, httphead

from gc import collect
from .. import logger
logger = logger.get("uRouter.request")


class Header(dict):
    def __init__(self, gen, *args, **kwargs):
        self.gen = gen
        super().__init__(*args, **kwargs)

    def __getitem__(self, key):
        if key not in self:
            # key not found.
            item: headeritem
            for item in self.gen:
                if item.key == key:
                    return item.value

        return super().__getitem__(key)

    def get(self, key, *args):
        if key not in self:
            # key not found.
            for item in self.gen:
                if item.key == key:
                    return item.value

        return super().get(key, *args)


class Request():
    host: str
    port: int
    uri: str
    url: str
    method: int
    http_version: str
    args: dict

    _client: socket.socket
    _headers: dict
    _form: dict

    def init(
        self,
        client: socket.socket,
        addr: tuple(str, bytes),
        head: httphead
    ):
        self._client = client
        # comp http first line.
        self.host, self.port = addr

        self._form = None

        self.method, self.uri, self.http_version = head

        self._hdgen = self._header_generate()
        self._headers = Header(self._hdgen)
        self.args = {}
        # Parsing uri to url

        pst = self.uri.find("?")
        if pst > -1:
            # 解析参数
            self.args = load_form_data(self.uri[pst+1:], self.args)
            self.url = self.uri[:pst]
        else:
            self.url = self.uri

    def _flush_header(self):
        """
        Flush header data.
        """
        try:
            while True:
                next(self._hdgen)
        except StopIteration:
            return  # flush over


    def _header_generate(self) -> str:
        """
        Generate headers lazily, reducing resource waste 
        it will return a header-item at once and append it to `_headers` automaticly.
        """
        line: str
        while True:
            line = self._client.readline()
            # filter the empty line
            if line:
                line = line.decode(CONFIG.charset).strip()
                # filter the \r\n already.
                if line:
                    # if it not None, it will be a header line.
                    pst = line.find(':')
                    key: str = line[:pst]
                    # content = line[pst+2:]
                    # tuple is more memory-saved
                    value = line[pst+2:].strip()
                    self._headers[key] = value
                    yield headeritem(key, value)
                else:
                    # if it is a empty line(just \r\n), it means that header line was generated out.
                    return
            else:
                return  # have no header, just return.

    @property
    def headers(self) -> dict:
        return self._headers

    def _load_form(self):
        # Content-Type: application/x-www-form-urlencoded
        # file1=EpicGamesLauncher.exe&file2=api-ms-win-core-heap-l1-1-0.dll

        # Content-Type: multipart/form-data:
        # POST / HTTP/1.1
        # Host: 127.0.0.1
        # Connection: keep-alive
        # Content-Length: 348
        # Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryOM7deWP2QaJYb9LE
        # Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
        # Accept-Encoding: gzip, deflate, br
        # Accept-Language: zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6

        # ------WebKitFormBoundaryOM7deWP2QaJYb9LE
        # Content-Disposition: form-data; name="file1"; filename="fl1.txt"
        # Content-Type: text/plain

        # This is file 1
        # ------WebKitFormBoundaryOM7deWP2QaJYb9LE
        # Content-Disposition: form-data; name="file2"; filename="fl2.txt"
        # Content-Type: text/plain

        # This is file 2
        # ------WebKitFormBoundaryOM7deWP2QaJYb9LE--

        if self._form:
            return

        content_type = self.headers.get(
            "Content-Type",
            "application/x-www-form-urlencoded"
        )

        if "multipart/form-data" in content_type:
            raise NotImplementedError("multipart/form-data was not implemented, \
                please use application/x-www-form-urlencoded method.")

        # flush the header content.
        self._flush_header()

        # application/x-www-form-urlencoded content like this
        # username=123456&passwd=admin

        # data = self._client.recv()
        # content = data.decode(CONFIG.charset)
        # items = content.split("&")
        # try to recv all data.
        items: list = self._client.recv()\
            .decode(CONFIG.charset)\
            .split("&")
        collect()

        for item in items:
            k, v = item.split("=")
            self._form[k] = v

    @property
    def form(self) -> dict:
        # 惰性加载 form, 只要你不用, 我就不加载.
        if not self._form:
            self._load_form()

        return self._form

    @property
    def client(self) -> socket.socket:
        self._flush_header()
        return self._client
