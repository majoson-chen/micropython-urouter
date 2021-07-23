import re
from urouter.consts import placeholder_func, empty_dict

from . import regexutil

from .typeutil import ruleitem

def make_path(paths: list) -> str:
    """
    把一个str的list合并在一起,并用 '/' 分割
    -> ['api','goods']
    <- "/api/goods"
    """
    if not paths:
        return '/'

    s = ''
    for i in paths:
        if i == '':
            continue  # 过滤空项
        s = '%s%s%s' % (s, '/', i)

    return s

def split_url(url: str) -> list:
    """
    将字符串URL分割成一个LIST

    -> '/hello/world'
    <- ['hello', 'world']
    """
    return [x for x in url.split("/") if x != ""]  # 去除数组首尾空字符串

def parse_url(url: str) -> str:
    """
        规范化 URL

    -> hello/world
    <- /hello/world
    """
    if url == "":
        url = "/"
    if not url.startswith('/'):
        url = "/%s" % url  # 添加开头斜杠
    # if not url.endswith ("/"): url += "/" # 添加末尾斜杠
    return url

def _translate_rule(rule: str) -> tuple:
    """
    将一个普通的路由字符串转化成正则表达式路由
    :param rule: 欲转化的规则文本
    :return (rule:str, url_vars:list)

    url_vars = [
        (var_name:str, vartype: class)
    ]
    例子:
    => '/'
    <= ('^//?(\\?.*)?$', [])
    """
    rule: list = split_url(parse_url(rule))
    url_vars: list = []  # 存放变量名称

    for i in rule:  # 对其进行解析
        m = re.match(regexutil.VAR_VERI, i)
        # m.group (1) -> string | float ...
        # m.group (2) -> var_name
        if m:
            # 如果匹配到了,说明这是一个变量参数
            var_type = m.group(1)
            if var_type == "string":
                # rule.index (i) 获取 i 在 l_rule 中的下标
                rule[rule.index(i)] = regexutil.MATCH_STRING
                url_vars.append((m.group(2),))
            elif var_type == "float":
                rule[rule.index(i)] = regexutil.MATCH_FLOAT
                url_vars.append((m.group(2), float))
            elif var_type == "int":
                rule[rule.index(i)] = regexutil.MATCH_INT
                url_vars.append((m.group(2), int))
            elif var_type == "path":
                rule[rule.index(i)] = regexutil.MATCH_PATH
                url_vars.append((m.group(2),))
            elif var_type.startswith("custom="):
                rule[rule.index(i)] = m.group(1)[7:]
                url_vars.append((m.group(2),))
            else:
                raise TypeError(
                    "Cannot resolving this variable: {0}".format(i))

    rule = "^" + make_path(rule) + "/?(\?.*)?$"

    return (rule, tuple(url_vars))

class RuleTree():
    tree: list  # [ruletasks]

    def __init__(self):
        """Create a rule-tree"""
        self.tree = []

    def append(
        self,
        rule: str,
        func: callable,
        weight: int,
        methods: iter
    ):
        """Append a item to rule-tree"""
        rule, url_vars = _translate_rule(rule)

        
        item = ruleitem(weight, re.compile(rule), func, methods, url_vars)
        self.tree.append(item)
        # ruleitem: "rule", "func", "weight", "methods", "url_vars"

    def match(self, url: str, method: int) -> tuple:
        """
        Search for the relevant rule.
        if hit, will return a tuple: (weight, func, {vars: value})
        if not, return None
        """
        result = None
        kw_args = {}
        item: ruleitem
        for item in self.tree:

            if method not in item.methods:
                # 访问方式不匹配,跳过
                continue
            

            result = item.comper.match(url)
            if result:
                # 有结果代表匹配到了

                # 检测是否有变量列表
                if item.url_vars:
                    try:
                        # 获取 result 中的所的组
                        idx = 1
                        while True:
                            var_tp = item.url_vars[idx-1]
                            # var_tp = (var_name, var_type)
                            # var_name = var_tp[0]

                            # 有类型则进行转化,无类型则跳过
                            if len(var_tp) == 2:  # 有类型
                                # 有类型则转化
                                value = var_tp[1](result.group(idx))
                            else:
                                # 无类型说明默认为str
                                value = result.group(idx)

                            # var_tp[0] 变量名
                            kw_args[var_tp[0]] = value
                            # 按顺序取出变量,放入kw_args中
                            idx += 1
                    except:
                        # 报错说明没了
                        ...

                return (item.weight, item.func, kw_args)
        # 没有被截胡说明没有被匹配到
        return (0 , placeholder_func , empty_dict)
