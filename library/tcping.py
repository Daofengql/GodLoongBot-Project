import time
from socket import *


class tcping(object):
    def tcping(self, ip, port):
        tcp_client_socket = socket(AF_INET, SOCK_STREAM)
        try:
            start_time = time.time() * 1000
            tcp_client_socket.connect((str(ip), int(port)))
        except:
            return float(20000)
        stop_time = time.time() * 1000
        tcp_client_socket.close()
        return round(float(stop_time - start_time), 2)
