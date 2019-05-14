import socket
import threading
from threading import Thread
class ThreadPoolManager():
    def __init__(self,thread_num):
        self.work_queue= Queue()
        self.thread_num=thread_num
        self.__init_threading_pool(self.thread_num)
    def __init_threading_pool(self,thread_num):
        for i in range(thread_num):
            thread=ThreadManager(self.work_queue)
            thread.start()
    def add_job(self,func,*args):
        self.work_queue.put((func,args))

class ThreadManager(Thread):
    def __init__(self,work_queue):
        Thread.__init__(self)
        self.work_queue=work_queue
        self.daemon=True
    def run(self):
        while True:
            target,args=self.work_queue.get()
            target(*args)
            self.work_queue.task_done()

thread_pool = ThreadPoolManager(4)
def handle_request(conn_socket):
    recv_data=conn_socket.recv(1024)
    reply=b'HTTP/1.1 200 OK \r\n\r\n'
    reply+=b'hello world'
    print('thread is running'%threading.current_thread().name)
    conn_socket.send(reply)
    conn_socket.close()

s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
while True:
    conn_socket,addr = s.accept()
    thread_pool.add_job(handle_request,*(conn_socket,))
s.close()
