# micropython-uRouter 开发文档

![LOGO](/cover.png)

## 阅读 [开发文档](https://urouter.m-jay.cn) 以获得更多信息

## 注意: 本框架目前正处于预览开发阶段, 如果在使用过程中遇到任何问题, 请前往提交 [issue](https://github.com/Li-Lian1069/micropython-urouter/issue)

<span style="color: #B06AB3"><strong>
如果您喜欢本项目, 或者本项目帮到了您, 麻烦给本项目点个 `star` 吧~</strong>
</span>

## I need help
I am not expert at English, so i need someone who is good at English helping me to translate the document into English.

## 这是什么

这是一个工作在 `micropython` 上的一个轻量, 简单, 快速的WEB框架.

**为什么要开发这个框架?**

据我所知, 目前已知的可以在 `micropython` 上运行的 web 框架有 [microWebSrv](https://github.com/jczic/MicroWebSrv) , 但是这个框架需要 `_thread` 模块的支持

但, 很遗憾的是, 在类似于 `esp8266` 这样的板子上并没有该模块的支持.

同时, 这个模块的运行需要阻塞主线程, 这就意味着你的开发版只能一味地处理HTTP请求, 而不能处理其他的事情.

因此, 我们需要一个支持单线程运行, 而且不会阻塞主线程的web框架, 于是这个框架应运而生.

## 特色功能:
本框架的开发以 `简洁`, `轻巧`, `易用`, `灵活`, `高效` 作为主旨.  

本模块有两种独特的工作模式:
- **normal-mode 普通工作模式**  
在此模式下本框架的处理是阻塞的, 即一切请求都会被阻塞并且等待  

- **dynamic-mode 动态工作模式**  
在此模式下本框架的处理是非阻塞的, 即检查浏览器请求的操作会立即被返回(理论上), 只有在处理HTTP请求的情况下会阻塞线程.  

### flask 风格的context上下文管理
本模块拥有类似于 `flask` 框架的 `context` 管理对象(即`request`, `response`, `session`), 减少学习成本, 简化开发流程  

### 魔法路径变量
本框架支持与Flask类似的魔法路径变量, 支持使用一个规则字符串匹配多个路径.

## 与 microWebSrv 的对比

| 特性/框架      | mpy_uRouter | microWebSrv |
| -------------- | ----------- | ----------- |
| python习惯命名 | *           |             |
| 单线程支持     | *           | *           |
| 多线程支持     |            | *           |
| 非阻塞支持     | *           |             |
| 多对象支持     | *           |             |
| 学习成本       | 低          | 高          |
| 复杂程度       | 简单        | 复杂        |

## 如何使用?
### 通过pypi安装
```python
# on mpy repl.
import upip

upip.install('micropython-uRouter')
upip.install('micropython-ulogger')
```

### 手动安装(推荐)
通过 `pypi` 下载的包是未经过编译的 `python` 源代码文件, `micropython` 支持将源代码文件进行编译以获得执行速度上的提升和体积上的缩小. 如果你的设备(例如`esp8266`) 在导入模块的过程中遇到内存分配失败的错误, 可以尝试使用此方式安装.

步骤:  
1. 先去本项目的 [release](https://github.com/Li-Lian1069/micropython-urouter/releases) 页面下载一个最新版本的打包版本
2. 将下载到的文件上传到开发版的 `/lib` 目录中. (可以使用 `thonny` ide)
3. 安装类似的步骤安装本框架的依赖库: https://github.com/Li-Lian1069/micropython-ulogger

### 快速开始
我们先来建立一个最简单的处理路由:
```python
# connect to network...

from urouter import uRouter
app = uRouter()

@app.route("/")
def index():
    return "<p>Hello World!<p>"

app.serve_forever()
```
这样, 当你在浏览器地址栏输入开发板的局域网ip并按下回车时, 你的浏览器就会显示出 `Hello World!` 了.

#### 监听其他访问方式
有时候你可能需要使用 `POST` 方式获取一些数据, 我们可以设置让本框架监听 `POST` 的访问方式:
```python
from urouter import uRouter, POST
app = uRouter()

@app.router("/login", methods=(POST,))
def login():
    request = app.request
    form = request.form
    if form.get("user_name") == 'admin' and form.get("passwd") == "admin":
        return "Login succeed!"
    else:
        return "Login failed, check your username or you password!"
```
在上面的例子中, 我们使用了 `request` 对象, 这个对象用来获取关于浏览器请求的一些信息, 例如 headers, 客户端地址, 访问方式等等. 我们使用的 `form` 对象就是从中获取的, `form` 对象是一个字典, 可以使用 `get` 方式来获取相应的数据.

注意我们使用了 `methods=(POST,)` 来指定监听方式为 `POST`, 这个 `POST` 对象是我们从 `urouter` 中导入的一个常量, 需要注意的是: `methods` 参数必须传入一个可迭代的对象(`list` 或者  `tuple`), 一般的情况下推荐使用 `tuple`(如果您不需要动态修改监听方式), 因为在成员数量固定的情况下, `tuple` 比 `list` 更加节省内存, 在嵌入式设备中内存是非常有限的, 我们要在最大程度上节省不必要的内存开支.


### 获取更多开发信息, 详见 [开发文档](https://urouter.m-jay.cn)

## 注意:
在使用本框架时, 应注意:
- 请不要在让本模块的监听和处理函数在多个线程中运行(即保持本框架工作在单线程模式), 你可以专门申请一个线程让他工作, 但是不要让他同时处理多件事情, 这会造成 `context` 对象的混乱.
例子:
```python
# connect to network...

from _thread import start_new_thread
from urouter import uRouter
app = uRouter()

@app.route("/")
def index():
    return "<p>Hello World!<p>"

start_new_thread(app.serve_forever)
# that is ok.

start_new_thread(app.serve_forever)
# Do not start two server.
```

```python
# connect to network...

from _thread import start_new_thread
from urouter import uRouter
app = uRouter()

@app.route("/")
def index():
    return "<p>Hello World!<p>"

while True:
    if app.check():
        start_new_thread(app.serve_once)
# Don't do that.
```
- 本模块可以同时拥有多个app实例, 可以同时工作(未经充分测试)
- 不要随意修改本框架的 `context` 对象(例如 `request` 和 `response`, `session`), 理论上, 您不应该修改任何未声明可以被修改的内容.

