import socket
import sys
import _thread
import time
from http import Response, Request

HOST = '127.0.0.1'
PORT = 6666

default_responseHdDict = {'Server': 'Python Socket Server', 'Developer': 'SXY'}


default_entityHdDict = {'Content_Encoding': 'utf-8', 'Content_Language': 'en', 'Content_Length': None,
                        'Content_Type': 'text'}


def generate_response(status, entity):
    response = Response()
    response.set_status(status)
    response.set_entity(entity)
    default_entityHdDict['Content_Length'] = str(len(entity))
    localtime = time.asctime(time.localtime(time.time()))  # 获取当地当前时间
    response.generalHd.set_datetime(localtime)
    response.responseHd.set_dict(default_responseHdDict)
    response.entityHd.set_dict(default_entityHdDict)
    return response


# 处理客户端发过来的请求报文字符串, 返回成请求报文的类实例
def get_request(raw_request):
    request = Request()
    request.unpack(raw_request)
    return request  # 返回一个类实例


class ServerConnect(socket.socket):
    def __init__(self, host, port):

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print('Socket created.')
        try:
            self.sock.bind((host, port))
            print('Socket bound.')
        except socket.error:
            print('Bind Failed.')
            sys.exit(0)
        self.sock.listen(5)
        print('Socket now listening...')
        self.users = {}



    def do_login(self, conn, userName):
        print(userName,'print username')
        name = userName.strip()
        # 查询用户名是否已存在
        if name in server.users:
            raw_response = generate_response('401', 'User Existed').pack()
            conn.sendall(raw_response)
        else:
            self.users[name] = conn
            raw_response = generate_response('200', 'OK and hello').pack()
            conn.sendall(raw_response)
            # 向所有其他用户广播, 有新的用户加入聊天室
            raw_response = generate_response('200',
                                            userName + ' has just entered the chat room...\n').pack()
            self.broadcast(userName, raw_response)

    def single_connect(self, conn, addr):
        print('Accept new connection from: %s, %s' % addr)
        raw_response = generate_response('202', 'connected').pack()
        conn.sendall(raw_response)
        while True:
            raw_request = conn.recv(4096)
            if not raw_request:
                continue
            print('raw request begin')
            print(bytes.decode(raw_request))
            print('raw request end')
            request = get_request(raw_request)
            user_name=request.requestHd.dic['User_Agent']
            person=request.request_single
            content=request.entity
            if request.request_type=='GETIN':
                self.do_login(conn,user_name)
            elif request.request_type=='EXIT':
                self.do_exit(conn,user_name)
                break
            elif request.request_type=='INQUIRY':
                self.do_query(conn)
            elif request.request_type=='POST':
                self.do_say(conn,user_name,content)
            elif request.request_type=='SINGLE':
                self.do_single(conn,user_name,person,content)


    # 向所有其他用户广播
    def broadcast(self, userName, content):
        for name, conn in self.users.items():
            if name != userName:
                conn.sendall(content)

    # 处理客户端退出聊天室的请求
    def do_exit(self, conn, userName):
        self.users.pop(userName)
        print('Connection from %s ended...' % userName)
        # 向所有其他用户广播, 该用户已经退出聊天室
        raw_response = generate_response('200',
                                        userName + ' has just left the chat room...\n').pack()
        self.broadcast(userName, raw_response)
        conn.close()

    def do_query(self, conn):
        result = 'Online users:\n'
        for key in self.users.keys():
            result += (key + '\n')
        raw_response = generate_response('200', result).pack()
        conn.sendall(raw_response)

    def do_say(self, conn, userName, content):
        # 向该用户返回所发送的聊天信息
        entity = ('[ ' + userName + ' ] : ' + content + '\n')
        raw_response = generate_response('200', entity).pack()
        conn.sendall(raw_response)
        # 向所有其他用户广播该用户的聊天信息
        raw_response = generate_response('200', '[ ' + userName + ' ] : ' + content + '\n').pack()
        self.broadcast(userName, raw_response)

    def do_single(self,conn,user_name,person,content):
        if person in self.users:
            entity = ('[ ' + user_name + ' to ' + person + ' ] : ' + content + '\n')
            response = generate_response('200', entity).pack()
            conn.sendall(response)
            # 向特定用户广播该用户的聊天信息
            raw_response = generate_response('200', '[ ' + user_name + ' to ' + person + ' ] : ' + content + '\n').pack()
            conn1=self.users[person]
            conn1.sendall(raw_response)
        else:
            response = generate_response('404', person+' not found').pack()
            conn.sendall(response)


if __name__ == '__main__':
    # 创建服务器主socket
    server = ServerConnect(HOST, PORT)

    try:
        while True:
            conn, addr = server.sock.accept()
            _thread.start_new_thread(server.single_connect, (conn, addr))
    except KeyboardInterrupt:
        print('Server shutdown...Done')
    finally:
        server.close()



