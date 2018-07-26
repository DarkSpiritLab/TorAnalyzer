import socket
localIP = "0.0.0.0"

def get_host_ip():
    # todo get ip from server not local
    '''
    get local ip
    :return:
    '''
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip
