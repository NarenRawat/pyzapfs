import socket

def create_udp_broadcast_socket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    return sock

def create_udp_broadcast_recv_socket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    return sock

def send_broadcast(sock, message):
    sock.sendto(message, ("255.255.255.255", 9000))


def create_tcp_socket(ip = None, port = None, backlog = 0):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


    if ip is not None and port is not None:
        sock.bind((ip, port))

        if backlog:
            sock.listen(backlog)

    return sock