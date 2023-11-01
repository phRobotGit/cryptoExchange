#%%
import socket 


class Server():
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
    
    def listening(self, response_body):
        self.socket.listen(1) # 设置等待未处理链接得的最大数量
        print('Serving HTTP on port %s ...' % self.port)
        while True:
            client_connection, client_address = listen_socket.accept()
            request = client_connection.recv(1024)
            print(request.decode("utf-8"))
            http_response = """
                HTTP/1.1 200 OK

                {response_body}
                """
            client_connection.sendall(http_response.encode("utf-8"))
            client_connection.close()
         