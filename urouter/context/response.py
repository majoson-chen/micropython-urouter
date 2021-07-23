#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   response.py
@Time    :   2021/07/10 23:40:35
@Author  :   M-Jay
@Contact :   m-jay-1376@qq.com

Used to respond to HTTP requests.
'''
import socket
import json

from ..util import dump_headers_generator, is_html
from ..config import CONFIG
from ..consts import STATU_CODES
from ..mimetypes import get as getmtp
from io import BytesIO
from os import stat

from .. import logger
logger = logger.get("uRouter.response")


class Response():
    _client: socket.socket
    _responsed: bool
    _header_sended: bool
    _buf: bytearray
    root_path: str

    headers: dict
    statu_code: int
    mime_type: str

    def __init__(self):
        self._buf = bytearray(1024)
        self.root_path = ""

    def init(
        self,
        client: socket.socket,
    ):
        # logger.debug("init response")

        self._client = client
        self._stream_mode = False
        self._responsed = False
        self._header_sended = False

        self.statu_code = 200
        # self.mime_type = "text/html; charset=%s" % CONFIG.charset
        self._mime_type = ""
        self.headers = {
            "Server": "uRouter on micropython",
        }

    @property
    def mime_type(self):
        return self._mime_type

    @mime_type.setter
    def mime_type(self, value: str):
        # mime_type can only be set once
        if self._mime_type:
            # set already.
            return
        else:
            self._mime_type = value

    def _flush(self):
        """
        Flush the data.
        """
        self._client.settimeout(0)
        while True:
            # flush
            try:
                if self._client.readinto(self._buf):
                    continue
                else:
                    # read-len == 0, flush over.
                    break
            except OSError:
                # have no data
                break

        self._client.settimeout(CONFIG.request_timeout)


    def _send_headers(self):
        """
        Send the headers, than you can send the data.
        It must be called after you use `redirect` or `setheader` or `set_statu_code`
        """

        if self._header_sended:
            return # don not repeaty send header.

        # send head line.
        self._client.send(
            # HTTP/1.1 200 OK
            ("%s %s %s\r\n" % (
                "HTTP/1.1",
                self.statu_code,
                STATU_CODES.get(self.statu_code)
            )).encode(CONFIG.charset)
        )

        if self.mime_type:
            self.headers["Content-Type"] = self.mime_type
        else:
            self.headers["Content-Type"] = "application/octet-stream"

        # send headers
        for header_line in dump_headers_generator(self.headers):
            self._client.send(header_line.encode(CONFIG.charset))
        # end headers

        self._client.send(b"\r\n")
        self._header_sended = True
        # logger.debug("header sended: ", self.headers)
        # content start.

    def abort(
        self,
        statu_code: str = 500,
    ):
        self.mime_type = "text/html"
        self.statu_code = statu_code
        self._send_headers()

    def redirect(
        self,
        location: str,
        statu_code: str = 302
    ):
        """
        Redirect the request.
        """
        assert not self._responsed, "Do not send response repeatily."

        self.headers["Location"] = location
        self.statu_code = statu_code
        self._send_headers()
        self._responsed = True

    def make_response(self, data: any) -> bool:
        """
        Send the response data, and close the response.
        * If your data length is specific, use it to make a response.
        * If not, please use stream-mode.
        """
        assert not self._responsed, "Do not send response repeatily."

        data = self.parse_data(data)
        self.headers["Content-Length"] = "%d" % len(data)
        self._send_headers()


        self._client.send(data)
        self._responsed = True

        # logger.debug("make response: ", data)
        return True

    def make_stream(self):
        """
        use stream-mode to send data.
        it can send the uncertain size data.
        """
        assert not self._responsed, "Do not send response repeatily."

        self.headers["Transfer-Encoding"] = "chunked"
        self._stream_mode = True
        self._stream_finish = False
        self._send_headers()
        self._responsed = True

        # logger.debug("make stream.")

    def finish_stream(self):
        """
        Finish the streaming and close the request.
        """
        self._client.send(b"0\r\n\r\n")
        # self._close()
        # logger.debug("finish stream.")
        self._stream_finish = True


    def send_data(self, data: bytes) -> int:
        """
        Send the data if you enabled the stream-mode
        """
        assert self._stream_mode, "This method just suit for stream-mode."

        data = self.parse_data(data)

        self._client.send(b"%x\r\n" % len(data))
        self._client.send(data)

        # logger.debug("send stream data: ", data)
        return self._client.send("\r\n")

    def send_file(self, path: str) -> bool:
        """
        Send the local file which in root_path.
        if file not-found in root-path, it will send 404 statu automaticly
        if send failed, it will return False

        :param path: the file name(reletive path suggested)
        """
        if path[0] != "/":  # must start with '/'
            path = "/%s" % path

        path = "%s%s" % (self.root_path, path)
        
        self._responsed = True

        try:
            file = stat(path)
        except:  # file not found.
            self.abort(404)
            # logger.debug("local file not found: ", path)
            return True


        if file[0] == 16384:  # If it is a folder, give up
            # TODO: send default file in this floder.
            self.abort(404)
            # logger.debug("local file not found: ", path)
            return True

        file_size = file[6]
        # 没报错就是找到文件了
        suffix = path[path.rfind('.'):]
        # 设定文档类型
        self.mime_type = getmtp(suffix.lower(), "application/octet-stream")
        self.headers["Content-Length"] = "%s" % file_size

        self._send_headers()
        # 分片传输文件
        with open(path, 'rb') as file:
            try:
                while file_size > 0:
                    x = file.readinto(self._buf)
                    if not self._client.write((
                        self._buf
                        if 
                        x == len(self._buf) 
                        else 
                        memoryview(self._buf)[:x]
                    )) == x:
                        logger.warn("The size of the sent data does not match: ", path)
                        return False
                    file_size -= x
            except OSError:
                # timeout
                logger.debug("Send local file timeout.")
            except Exception as e:
                logger.debug("Faild to send local file: ", e)
                return False

        logger.debug("send local file: ", path)
        return True

    def parse_data(self, data) -> bytes:
        """
        pass in a str, bytes, bytearray , number, BytesIO obj.
        return a buffer to send data.

        :param arg: [description]
        :type arg: [type]
        """


        # if isinstance(data, str):
        #     if data.find("<html>"):
        #         self.mime_type = "text/html; charset=%s" % CONFIG.charset
        #     else:
        #         self.mime_type = "text/plain; charset=%s" % CONFIG.charset
        # elif isinstance(data, (bytes, bytearray, BytesIO)):
        #     self.mime_type = "application/octet-stream"

        if isinstance(data, str):
            self.mime_type = (
                "text/html; charset=%s" % CONFIG.charset
                if is_html(data)
                else "text/plain; charset=%s" % CONFIG.charset
                )
            data = data.encode(CONFIG.charset)
        elif isinstance(data, (bytes, bytearray)):
            pass  # Acceptable type
        elif isinstance(data, (tuple, list, dict)):
            self.mime_type = "application/json"
            data = json.dumps(data).encode(CONFIG.charset)
        elif isinstance(data, int, float):
            self.mime_type = "text/plain"
            data = b"%s" % data
        elif isinstance(data, BytesIO):
            data: BytesIO
            self.mime_type = "application/octet-stream"
            data = memoryview(data.getvalue())  # Avoid additional memory allocation.
        else:
            raise TypeError("Unknown response type.")

        return data
