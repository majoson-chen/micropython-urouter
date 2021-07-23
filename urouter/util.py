from .config import CONFIG
from .consts import *


def catch_chars(string: str) -> str:
    """
    将转化过的html还原
    :param string: 可以是一个 str, 也可以是一个 list[str]
    :return 输入 str 类型返回 str 类型 , 输入 list 类型返回 list 
    例如:
    escape_chars ("hello&nbspworld") -> "hello world"
    """

    if type(string) == str:
        for k, v in HTML_ESCAPE_CHARS.items():
            string = string.replace(k, v)
    elif type(string) == list:
        for k, v in HTML_ESCAPE_CHARS.items():
            for idx in range(len(string)):
                string[idx] = string[idx].replace(k, v)
    return string


def load_form_data(data: str, obj: dict):
    """
    传入一个bytes或者str, 将其解析成Python的dict对象, 用于解析HTML的表单数据
    例如:
    load_form_data ("user_name=abc&user_passwd=123456")
    -> {
        "user_name"   : "abc",
        "user_passwd" : "123456"
    }
    """
    if type(data) == bytes:
        data = data.decode(CONFIG.charset)

    data: list = data.split("&")

    if not data == ['']:  # data 有数据时再进行解析
        data = catch_chars(data)
        for line in data:
            idx = line.find("=")
            # arg_name  : line [:idx]
            # arg_value : line [idx+1:]
            obj[line[:idx]] = line[idx+1:]
    return obj


def dump_headers_generator(headers: dict):
    """
    Create a generator from headers.
    when you generated it , it will return a header line.
    """
    for k, v in headers.items():
        if isinstance(v, (tuple, list)):
            # transform the tuple to str.
            yield "%s%s%s%s" % (k, ": ", '; '.join(v), "\r\n")
        else:
            yield "%s%s%s%s" % (k, ": ", v, "\r\n")

    return


def is_html(string: str) -> bool:
    """
    Check whether if it was a html type.
    """

    if string.find("<html>"):
        return True
    elif string.find("<p>"):
        return True
    elif string.find("<div>"):
        return True
    elif string.find("<span>"):
        return True
    elif string.find("<h1>"):
        return True

    return False