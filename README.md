# micropython-urouter
 A lightweight HTTP request routing processing support library based on micropython.  
 The previous name was [micro-route](https://github.com/Li-Lian1069/micro_route)

算法:
1. 队列先进的先被执行
2. 可以根据重要程度设置优先级
使用两个队列来保存任务 (VIP任务, 普通任务)

特色:
非阻塞式
HTTP\websocket 二合一
装饰器定义路由
闲时队列调度算法
基于heap二叉树的优先调度
针对嵌入式设备设计的路由结构