import select
import socket



class Pool:
    _host: socket.socket
    _pool: select.poll

    max: int
    quantity: int # 连接数量
    def __init__(
        self, 
        host: socket.socket,
        max: int
        ):
        self._host = host
        self.max = max
        self.quantity = 0

        self._pool = select.poll()
        self._pool.register(host, select.POLLIN | select.POLLERR)

    def check(self):
        """Check the new request or new connetcions, and append them into Queue.
        """

    
        