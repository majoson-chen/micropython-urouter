try:
    from micropython import const
except:
    const = lambda x:x

GET     = "GET"
POST    = "POST"
HEAD    = "HEAD"
PUT     = "PUT"
OPINOS  = "OPINOS"
DELETE  = "DELETE"
TRACE   = "TRACE"
CONNECT = "CONNECT"

NORMAL_MODE = const(100)
DYNAMIC_MODE = const(200)

HTML_ESCAPE_CHARS = {
    "&amp;"   :  "&",
    "&quot;"  :  '"',
    "&apos;"  :  "'",
    "&gt;"    :  ">",
    "&lt;"    :  "<",
    "&nbsp"   :  " "
}

STATU_CODES:dict = {
    200 : 'OK', # 客户端请求成功
    201 : 'Created', # 请求已经被实现，而且有一个新的资源已经依据请求的需要而创建，且其URI已经随Location头信息返回。
    301 : 'Moved Permanently', # 被请求的资源已永久移动到新位置，并且将来任何对此资源的引用都应该使用本响应返回的若干个URI之一
    302 : 'Found', # 在响应报文中使用首部“Location: URL”指定临时资源位置
    304 : 'Not Modified', # 条件式请求中使用
    403 : 'Forbidden', # 请求被服务器拒绝
    404 : 'Not Found', # 服务器无法找到请求的URL
    405 : 'Method Not Allowed', # 不允许使用此方法请求相应的URL
    500 : 'Internal Server Error', # 服务器内部错误
    502 : 'Bad Gateway', # 代理服务器从上游收到了一条伪响应
    503 : 'Service Unavailable', # 服务器此时无法提供服务，但将来可能可用
    505 : 'HTTP Version Not Supported' # 服务器不支持，或者拒绝支持在请求中使用的HTTP版本。这暗示着服务器不能或不愿使用与客户端相同的版本。响应中应当包含一个描述了为何版本不被支持以及服务器支持哪些协议的实体。
}

empty_dict = {}
def placeholder_func():
    ...