import multiprocessing as mp
import socket,sys,hashlib,datetime,os
CH3PORT=8848
ACCESS=('root','A','B','C','D')
ACCESS_VALUE={'root':0,'A':1,'B':2,'C':3,'D':4}
access_list={}

ACCESS_DENIED=0
ACCESS_GRANTED=1
FILE_NOT_FOUND=2
NON_ERROR=3
RUNTIME_ERROR=4
FILE_EXISTS_ERROR=5

last_stat=3
def get_last():return last_stat
def set_last(n=3):
    global last_stat
    last_stat=n
def strip_list(lst):
    for i in range(len(lst)):
        lst[i]=lst[i].strip()
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
        access_list.update({user:User(user,pswd,access.strip())})
def check_file(file,mode='get'):
    q=os.getcwd()+'/CH3_Reference_Library'
    for c in file[:-1]:
        q+='/'+c
        if not os.path.isdir(q):
            set_last(FILE_NOT_FOUND)
            return False
    q+='/'+file[-1]
    if mode=='get' and not os.path.isfile(q) and os.path.isdir(q):
        return 'dir in '+q+' :\n'+'\n'.join(os.listdir(q))
    elif mode=='set':
        pass
    else:
        set_last(FILE_NOT_FOUND)
        return False
    set_last()
    return True
def access_file(cmd,user,file):
    file_=file[0].split('-')
    nowdir=os.getcwd()+'/CH3_Reference_Library/'
    can_access=ACCESS[ACCESS_VALUE[user.access]:]
    if cmd=='get':
        if file_[0] not in can_access:
            set_last(ACCESS_DENIED)
            return False
        ret=check_file(file_)
        if get_last()!=3 or isinstance(ret,str):return ret
        f=open(nowdir+'/'.join(file_))
        ret=f.read()
        f.close()
        set_last(ACCESS_GRANTED)
        return ret
    if cmd=='updata':
        if len(file)>3:
            set_last(RUNTIME_ERROR)
            return False
        ret=check_file(file_,'set')
        if get_last()!=3 or isinstance(ret,str):return ret
        if len(file)==1:
            try:
                os.mkdir(nowdir+'/'.join(file_))
                set_last(ACCESS_GRANTED)
                return True
            except FileExistsError:
                set_last(FILE_EXISTS_ERROR)
                return False
        f=open(nowdir+'/'.join(file_),mode='a+')
        print(file)
        f.write(file[1])
        f.close()
        set_last(ACCESS_GRANTED)
        return ret
def check_ret(ret,user):
    r=''
    if get_last()!=3:
        r='Unknow Error\n'
        if get_last()==ACCESS_DENIED:
            log('warning',user.name+' access denied')
            r='Access Denied\n'
        elif get_last()==ACCESS_GRANTED:
            log('warning',user.name+' access granted')
            r='Access Granted\n'
        elif get_last()==FILE_NOT_FOUND:
            log('warning',user.name+' access file not found')
            r='File Not Found\n'
        elif get_last()==RUNTIME_ERROR:
            log('error','Run Time Error!')
            r='Run Time Error\n'
        elif get_last()==FILE_EXISTS_ERROR:
            log('error','File Exists Error!')
            r='File Exists Error\n'
        else:
            pass
        set_last()
    if isinstance(ret,bool) or not ret:ret=''
    return r+ret+'\n'
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
    user=access_list[ms[0]]
    while True:
        strs=conn.recv(1024).decode('utf-8')
        if strs=='BYEBYE':
            conn.send(b'GOODBYE')
            conn.close()
            return True
        else:
            command=strs.split()
            if command:
                strip_list(command)
                if len(command)==1:
                    pass
                elif len(command)>=2:
                    r=check_ret(access_file(command[0],user,command[1:]),user)
                    conn.send(r.encode('utf-8'))
                else:
                    pass
def loop():
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.bind(('',CH3PORT))
    read_access()
    log('info','server start')
    try:
        while True:
            s.listen()
            conn,ht=s.accept()
            p=mp.Process(target=handle,args=(conn,ht))
            p.start()
    except KeyboardInterrupt:
        log('info','server shutdown')
        s.close()
        return
if __name__=='__main__':
    loop()
    
    
    