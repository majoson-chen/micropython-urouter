import socket


def test():
    clients = []
    host = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Fastely reuse-tcp
    host.bind(("0.0.0.0", 8848))
    host.listen(0)

    while True:
        try:
            client, addr = host.accept()
            clients.append(client)
            print("Accept: ", addr)
        except OSError:
            # max connect.
            print("test over, The max connection quantity is: ", len(clients))
            host.close()
            for sock in clients:
                try:
                    sock.close()
                except:
                    pass
            return
        