# 客户端实现简单的聊天登陆和登出的界面
# 客户端实现的主要功能有，接收他人发送信息，发送信息，查看在线情况等

import socket
import _thread
import wx
import time
from time import sleep
from http import Request, Response


Host = None # string
Port = None # int
User_name = None # string


# 发送头部的默认值
default_requestHdDict = {'Accept': 'text', 'Accept_Language': 'en/ch', 'Accept_Encoding': 'utf-8',
                         'Host': None, 'User_Agent': None}


default_entityHdDict = {'Content_Encoding': 'utf-8', 'Content_Language': 'en',
                        'Content_Length': None, 'Content_Type': 'text'}

""" 
将收到的报文进行处理
解析到具体的数据结构中方便进一步操作
函数调用http文件中的unpack文件
"""


def get_message(raw_data):
    print('getin')
    res=Response()
    res.unpack(raw_data)
    return res # 返回一个respones类

# 整合request信息生成request Message以便发送


def generate_message(request_type, request_single,  requestHead_dict,
                entityHead_dict, entity, http_version = 'HTTP/1.1'):
    req=Request()
    req.set_type(request_type)
    req.set_person(request_single)
    localtime = time.asctime(time.localtime(time.time()))  # 获取当地当前时间
    req.generalHd.set_datetime(localtime)
    req.requestHd.set_dict(requestHead_dict)
    if entity is None:
        entityHead_dict['Content_Length'] = 0
    else:
        entityHead_dict['Content_Length'] = str(len(entity))
        # 根据entity的长度设置entityhead中的content_length，打包的时候需要所有的部分都是str格式
    req.entityHd.set_dict(entityHead_dict)
    req.set_entity(entity)
    req.http_version=http_version
    return req


class LoginFrame(wx.Frame):  # 登陆界面
    def __init__(self, parent, title):

        wx.Frame.__init__(self, parent, title=title, size=(500, 400),
                          style=wx.DEFAULT_FRAME_STYLE ^ (wx.RESIZE_BORDER | wx.MINIMIZE_BOX | wx.MAXIMIZE_BOX))
        self.Center() # 窗体居中显示
        self.serverHostLabel = wx.StaticText(self, label='Server Host: ', pos=(10, 30), size=(100, 50))
        self.serverPortLabel = wx.StaticText(self, label='Server Port: ', pos=(10, 60), size=(100, 50))
        self.userNameLabel = wx.StaticText(self, label='User Name:', pos=(10, 90), size=(100, 50))
        self.serverHost = wx.TextCtrl(self, pos=(100, 30), size=(150, 25), value='127.0.0.1')  # 设置host默认值
        self.serverPort = wx.TextCtrl(self, pos=(100, 60), size=(150, 25), value='6666')  # 设置port默认值
        self.userName = wx.TextCtrl(self, pos=(100, 90), size=(150, 25), value='sxy')
        self.loginButton = wx.Button(self, label='Login', pos=(80, 145), size=(130, 30))
        self.loginButton.Bind(wx.EVT_BUTTON, self.login)
        self.Show()

    def login(self,event):
        while True:
            # 给全局变量port和host赋值
            global Host, Port, User_name
            Host=str(self.serverHost.GetLineText(0))
            Port=int(self.serverPort.GetLineText(0))
            User_name=str(self.userName.GetLineText(0))
            if User_name=='':
                self.show_dialog('User name cannot be empty', 'Error')
                continue
            if ' ' in User_name:
                self.show_dialog('User name cannot contain blank', 'Error')
                continue
            # 三个全局变量设置完毕，可以更新default_head
            global default_requestHdDict
            default_requestHdDict['Host']=Host
            default_requestHdDict['User_Agent']=User_name
            break

        if not client0.connected:
            try:
                # 连接server
                client0.open(host=Host, port=Port, timeout=10)
                raw_response = client0.receive_message()
                print( bytes.decode(raw_response),'\n') # 这里是一个格式处理，bytes格式转为str格式打印
                response= get_message(raw_response)
                if response.status_code!='202':
                    self.show_dialog('bad status', 'Error')
                # 生成要发送的heads
                request=generate_message('GETIN', None, default_requestHdDict, default_entityHdDict, '')
                # 发送进入聊天室的请求
                re=request.pack()
                client0.send_message(re)
                raw_response = client0.receive_message()
                print(bytes.decode(raw_response),'\n')
                response=get_message(raw_response)
                if response.status_code in ['400', '401', '500']:
                    self.show_dialog(response.state_name, 'Error')
                    self.Close()
                    return
                elif response.status_code=='200':
                    self.Close()
                    ChatFrame(None, title='<<MY_Chatting Room>>', size=(660, 500))
                else:
                    print(response.status_code + ': ' + response.state_name)
                    raise Exception
            except socket.error:
                self.show_dialog('Socket connection failed', 'error')
                self.Close()
                return


            '''except Exception:
                self.show_dialog('Unknown error', 'error')
                return
                '''

    def show_dialog(self, content, title):  # error message

        dialog = wx.MessageDialog(self, content, title, wx.OK | wx.CANCEL | wx.ICON_ERROR)
        dialog.Center()
        if dialog.ShowModal() == wx.ID_OK:
            dialog.Destroy()


class ChatFrame(wx.Frame):
    def __init__(self, parent, title, size):
        """
        聊天界面
        """
        wx.Frame.__init__(self, parent, title=title, size=size,
                          style=wx.DEFAULT_FRAME_STYLE ^ (wx.RESIZE_BORDER | wx.MINIMIZE_BOX |
                                                          wx.MAXIMIZE_BOX))
        self.Center()
        self.chatFrame = wx.TextCtrl(self, pos=(5, 5), size=(500, 310),
                                     style=wx.TE_MULTILINE | wx.TE_READONLY)

        self.show_name=wx.StaticText(self, label=User_name, pos=(550, 160), size=(150 ,50))
        font=wx.Font()
        font.SetPointSize(14)
        font.SetStyle(wx.FONTSTYLE_ITALIC)
        self.show_name.SetFont(font)
        self.messageLabel = wx.StaticText(self, label='Please Enter: ', pos=(5, 320), size=(150 ,25))
        self.message = wx.TextCtrl(self, pos=(5, 350), size=(300, 25))
        self.sendButton = wx.Button(self, label='Send', pos=(310, 345), size=(58, 25))  # 发送消息
        self.usersButton = wx.Button(self, label='Users', pos=(373, 345), size=(58, 25))  # 查询当前用户
        self.closeButton = wx.Button(self, label='Close', pos=(436, 345), size=(58, 25))  # 关闭聊天
        self.singleButton= wx.Button(self, label='Single_send', pos=(499, 345), size=(120, 25))  # 私戳
        self.to_label=wx.StaticText(self, label='To', pos=(499, 380), size=(25, 25))
        self.person = wx.TextCtrl(self, pos=(530, 380), size=(89, 25)) #私戳人名
        self.sendButton.Bind(wx.EVT_BUTTON, self.send_message)
        self.usersButton.Bind(wx.EVT_BUTTON, self.query_users)
        self.closeButton.Bind(wx.EVT_BUTTON, self.close)
        self.singleButton.Bind(wx.EVT_BUTTON, self.single_send)
        _thread.start_new_thread(self.receive_message, ())  # 创建另一个线程用来不停的接收消息
        self.Show()

    def send_message(self, event):
        message=str(self.message.GetLineText(0).strip())
        if message=="":
            self.show_dialog('message cannot be blank!', 'Oops')
        else:
            post=generate_message('POST',None, default_requestHdDict, default_entityHdDict, message)
            """
            request_type, requestHead_dict, entityHead_dict, entity, http_version = 'HTTP/1.1'
            """
            client0.send_message(post.pack())
            self.message.Clear()  # 发送之后删除文本框内容
    """
    
    """
    def query_users(self, event):
        query=generate_message('INQUIRY',None, default_requestHdDict, default_entityHdDict, '')
        """
        request_type, requestHead_dict, entityHead_dict, entity, http_version = 'HTTP/1.1'
        """
        client0.send_message(query.pack())

    def receive_message(self):
        while True:
            sleep(0.5)
            try:
                raw_response=client0.receive_message()
                print(bytes.decode(raw_response))
                response=get_message(raw_response)
                if response.entity != '' and response.status_code=='200':
                    self.chatFrame.AppendText(response.entity)
                    self.chatFrame.AppendText('\n')
                elif response.status_code!='200':
                    self.show_dialog(response.entity,'Oops,error')
            except socket.error:
                continue

    def close(self, event):
        message=generate_message('EXIT',None, default_requestHdDict, default_entityHdDict, '')
        client0.send_message(message.pack())
        client0.close()
        self.Close()

    def single_send(self,event):
        message = str(self.message.GetLineText(0).strip())
        if message == "":
            self.show_dialog('message cannot be blank!', 'Oops')
            return
        person= str(self.person.GetLineText(0))
        message=generate_message('SINGLE',person, default_requestHdDict, default_entityHdDict, message)
        client0.send_message(message.pack())
        self.message.Clear()
        self.person.Clear()


    def show_dialog(self, content, title):  # error message

        dialog = wx.MessageDialog(self, content, title, wx.OK | wx.CANCEL | wx.ICON_ERROR)
        dialog.Center()
        if dialog.ShowModal() == wx.ID_OK:
            dialog.Destroy()



class ChatConnect(socket.socket):

    def __init__(self):
        socket.socket.__init__(self)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False

    # 打开socket连接
    def open(self, host, port, timeout=10):
        self.sock.connect((host, port))
        self.sock.settimeout(timeout)
        self.connected = True

    # 关闭socket连接
    def close(self):
        self.sock.close()
        self.connected = False

    # 接收信息
    def receive_message(self):
        return self.sock.recv(4096)

    # 发送信息
    def send_message(self, message):
        self.sock.sendall(message)


if __name__ == '__main__':
    app = wx.App()
    client0 = ChatConnect()
    LoginFrame(None, title='Login')
    app.MainLoop()