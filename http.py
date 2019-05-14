
# request_type=['INQUIRY','POST','GETIN','EXIT','SINGLE']
#报文分成以上几种不同的类型
#'INQUIRY',查询当前在线的用户
# 'POST',发布消息
# 'GETIN',进入聊天室
# 'EXIT'，退出聊天室
responses = {'200': 'OK',
             '202': 'Accept',
             '400': 'Bad Request',
             '401': 'User Name Exist',
             '404': 'Not Found',
             '500': 'Internal Server Error'}
#首先定义头部的类
class Head:
    def __init__(self):
        self.dic=dict()
    def pack(self):
        ret=''
        for key, value in self.dic.items():
            ret += str(key)
            ret += ': '
            ret+= str(value)
            ret+='\n'
        return ret
    def unpack(self,str_data):
        for line in str_data:
            #print(line)
            key_value=line.split(': ',1)#分割一次，将value与键值分开

            self.dic[key_value[0]]=key_value[1]
    def set_dict(self,dict):
        self.dic=dict

class GeneralHd(Head):

    def __init__(self):
        Head.__init__(self)
        self.dic['Datetime']=None #通用头部包含时间

    def set_dict(self,dict):
        super().set_dict(dict)

    def set_datetime(self,datetime):
        self.dic['Datetime']=datetime

class RequestHd(Head):
    def __init__(self):
        Head.__init__(self)
        self.dic['Accept'] = None #request的键值，表示客户端接受的信息类型，如text
        self.dic['Accept_language']=None#request的键值，表示客户端接受的自然语言类型，如en(english)
        self.dic['Accept_Encoding']=None#request的键值，表示客户端接受的编码类型，如utf-8
        self.dic['Host'] =None#request的键值，表示主机
        self.dic['User_Agent']=None#表示处于客户端的用户

    def set_dict(self,dict):
        super().set_dict(dict)


class ResponseHd(Head):
    def __init__(self):
        Head.__init__(self)
        self.dic['Server']=None#服务器名
        self.dic['Developer']=None#开发者姓名
    def set_dict(self,dict):
        super().set_dict(dict)

class EntityHd(Head):
    def __init__(self):
        Head.__init__(self)
        self.dic['Content_Encoding']=None
        self.dic['Content_Language']=None
        self.dic['Content_Length']=None
        self.dic['Content_Type']=None
    def set_dict(self,dict):
        super().set_dict(dict)

class CHTTP: #chat_http传输的大类，包括头部

    def __init__(self):
        self.http_version = 'HTTP/1.1'
        self.generalHd=GeneralHd()
        self.entityHd=EntityHd()
        self.entity=None

    def set_entity (self , entity):
        self.entity=entity

class Request(CHTTP):

    def __init__(self):
        CHTTP.__init__(self)
        self.request_type=None #request的类型
        self.request_single=None #特定发给某人
        #  self.URI=None #URI:统一资源标志符
        self.requestHd=ResponseHd()

    def set_type(self,type):
        self.request_type=type

    def set_person(self,person):
        self.request_single=person


    def pack(self):
        ret=''
        ret+=self.request_type
        ret+=' '
        if self.request_single is not None:

            ret+=self.request_single
        else:
            ret+='*'
        ret+=' '
        ret+=self.http_version
        ret+='\n'
        ret+= self.generalHd.pack()
        ret+= self.requestHd.pack()
        ret+= self.entityHd.pack()
        ret+= self.entity
        ret += '\n'
        return str.encode(ret) #python3以bytes的形式处理数据

    def unpack(self, data):
        lines=bytes.decode(data).split('\n')

        temp=lines[0].split(' ')
        self.request_type=temp[0]
        self.request_single =temp[1]
        self.http_version = temp[2]
        self.generalHd.unpack((lines[1],))
        self.requestHd.unpack(lines[2:7])
        self.entityHd.unpack(lines[7:11])
        self.entity=' '.join(lines[11:])

class Response(CHTTP):
    def __init__(self):
        super().__init__()
        self.status_code= None #状态码
        self.state_name=None #状态码的名称/解释
        self.responseHd=ResponseHd()

    def set_status(self,code):
        self.status_code=code
        self.state_name=responses[code]

    def pack(self):
        ret=''
        ret+=self.http_version
        ret+=' '
        ret+=self.status_code
        ret+=' '
        ret+=self.state_name
        ret+='\n'
        ret+=self.generalHd.pack()
        ret+=self.responseHd.pack()
        ret+=self.entityHd.pack()
        ret+=self.entity
        ret+='\n'
        return str.encode(ret) # python3以bytes的形式处理数据

    def unpack(self,data):
        lines=str(bytes.decode(data)).split('\n')
        t=lines[0].split(' ')
        self.http_version=t[0]
        self.status_code=t[1]
        self.state_name=t[2]
        self.generalHd.unpack((lines[1],)) #转化为list
        self.responseHd.unpack(lines[2:4])
        self.entityHd.unpack(lines[4:8])
        self.entity=' '.join(lines[8:])
