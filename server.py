import socket
import sys
from threading import Thread

def child_connection(index, sock, connection):
    try:
        print("begin connection",index)
        print("begin connection%d"%index)
        connection.settimeout(50)
        #获得一个连接，循环处理此连接收到的消息，设置最大的时间长度限制
        while True:
            buf=connection.recv(1024)
            print('Get value %s from connection %d:'%(buf, index))
            if buf=='1':
                print("send welcome")
                connection.send(b'welcome')
                connection.send(b'welcome to server!')
            elif buf!='0':
                connection.send(b'please go out')
                print('send refuse')
            else:
                print('close')
                break
    except socket.timeout:
        print('time out')

    print('closing connection%d'%index)
    connection.close()
    Thread.exit_thread()



if __name__=="__main__":
    print("server is starting")
    sock=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    HOST = '127.0.0.1'
    PORT = 65432
    sock.bind((HOST, PORT))
    sock.listen(5)
    print("server is listening")
    index=0
    while True:
        connection, address=sock.accept()
        index+=1
        Thread.start_new_thread(child_connection(index, sock, connection))
        if index>10:
            break
    sock.close()

