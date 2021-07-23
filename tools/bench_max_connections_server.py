if __name__ == "__main__":

    host = input("[i] Input your board host: ")

    import socket
    clients = []
    import time
    while True:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Fastely reuse-tcp
        client.settimeout(10)
        try:
            client.connect((host, 8848))
            clients.append(client)
            time.sleep(0.3)
        except:
            print("test over.")
            for sock in clients:
                try:
                    sock.close()
                except:
                    pass
            break

    