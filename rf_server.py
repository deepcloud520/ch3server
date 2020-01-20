import multiprocessing as mp
import socket,sys,hashlib,datetime

CH3PORT=45668

access_list={}
def log(mode,info):
    d=datetime.datetime.now()
    strs='[%s]%s.%s %s:%s:%s %s\n' %(mode,d.month,d.day,d.hour,d.minute,d.second,info)
    f=open('ch3log.log',mode='a')
    f.write(strs)
    f.close()
    print(strs,end='')
class User:
    def __init__(self,name,passwd,access):
        self.name=name
        self.passwd=passwd
        self.access=access
    def login(self,passwd):
        if self.passwd==passwd:
            return True
        return False
def read_access():
    f=open('access')
    res=f.readlines()
    f.close()
    for line in res:
        user,pswd,access=line.split('$')
        access_list.update({user:User(user,pswd,access)})
def handle(conn,ht):
    global access_list
    log('info',ht[0]+' connect.')
    conn.send(b'''
    +---------Message----------+
    |   Welcome to ch3 server! |
    |     Made by SWWM,2020    |
    +--------------------------+    
    ''')
    ms=conn.recv(1024).decode('utf-8').strip().split('$')
    if len(ms)==1:
        conn.send(b'LOGIN FAILED.SHUTDOWN HANDLE')
        conn.close()
        log('warning',ht[0]+' send data struct can\'t handle')
        return False
    if ms[0] not in access_list or not access_list[ms[0]].login(ms[1]):
        conn.send(b'LOGIN FAILED.SHUTDOWN HANDLE')
        conn.close()
        log('warning',ht[0]+' use '+ms[0]+' '+ms[1]+' login Failed')
        return False
    conn.send(b'LOGIN SUCCESS')
    log('info',ht[0]+' login success')
    while True:
        strs=conn.recv(1024).decode('utf-8')
        if strs=='BYEBYE':
            conn.send(b'GOODBYE')
            conn.close()
            return True
        else:
            command=strs.split()
            if command:
                if len(command)==1:pass
                elif len(command)==2:
                    if command[0]=='get':
                        pass
                else:
                    pass
def loop():
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.bind(('',CH3PORT))
    read_access()
    log('info','server start')
    while True:
        s.listen()
        conn,ht=s.accept()
        p=mp.Process(target=handle,args=(conn,ht))
        p.start()
if __name__=='__main__':
    loop()
    
    
    