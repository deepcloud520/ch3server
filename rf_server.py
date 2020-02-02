import multiprocessing as mp
import socket,sys,time,datetime,os,base64
from RSA import *
CH3PORT=12320
ACCESS=('Root','A','B','C','D')
ACCESS_VALUE={'Root':0,'A':1,'B':2,'C':3,'D':4}
access_list={}
class User:
    def __init__(self,name,passwd,access):
        self.name=name
        self.passwd=passwd
        self.access=access
    def login(self,passwd):
        if self.passwd==passwd:
            return True
        return False
    def copy(self):return User(self.name,self.passwd,self.access)
    def __str__(self): return '{name:'+self.name+',passwd:'+self.passwd+',access:'+self.access+'}'
ACCESS_DENIED=0
ACCESS_GRANTED=1
FILE_NOT_FOUND=2
NON_ERROR=3
RUNTIME_ERROR=4
FILE_EXISTS_ERROR=5
CHECK_FAILED=6
START_CLOCK=0
LAST_USER=User('','','')
NOW_USER=User('','','')

last_stat=3
def get_last():return last_stat
def set_last(n=3):
    global last_stat
    last_stat=n
def strip_list(lst):
    for i in range(len(lst)):
        lst[i]=lst[i].strip()
#struct:month,day,hour,minute,second,nowsecond,canruntime(minute,conv to second),uname,uaccess,tgname,tgaccess,canruncmd
def genenum(user,targetuser,can_run_cmd=10,can_run_time=10):
    d=datetime.datetime.now()
    st=':'.join((str(d.month),str(d.day),str(d.hour),str(d.minute),str(d.second),str(int(time.time())),str(int(can_run_time)*60),user.name,user.access,targetuser.name,targetuser.access,str(can_run_cmd)))
    data=base64.b64encode(st.encode('utf-8')).decode('utf-8')
    return data
def checknum(num,user,target):
    de_=base64.b64decode(num.encode('utf-8')).decode('utf-8').split(':')
    if de_[5]==user.name and de_[6]==user.access and de_[7]==target.name and de_[8]==target.access and int(de_[5])+int(de_[6])<=int(time.time()):
        set_last(ACCESS_GRANTED)
        return de_
    set_last(CHECK_FAILED)
    return 0
def log(mode,info):
    d=datetime.datetime.now()
    strs='[%s]%s.%s %s:%s:%s %s\n' %(mode,d.month,d.day,d.hour,d.minute,d.second,info)
    f=open('ch3log.log',mode='a')
    f.write(strs)
    f.close()
    print(strs,end='')
def read_access():
    f=open('access')
    res=f.readlines()
    f.close()
    for line in res:
        user,pswd,access=line.split('$')
        access_list.update({user:User(user,pswd,access.strip())})
def listdir(file):
    strs='dir in '+file+':\n'
    for n in os.listdir(file):
        strs+= n+'\t<dir>\n' if os.path.isdir(file+'/'+n) else n+'\n'
    return strs 
def check_file(file,mode='get'):
    q=os.getcwd()+'/CH3_Reference_Library'
    for c in file[:-1]:
        q+='/'+c
        if not os.path.isdir(q):
            set_last(FILE_NOT_FOUND)
            return False
    q+='/'+file[-1]
    if mode=='get' and os.path.isdir(q):
        return listdir(q)
    elif mode=='set':
        pass
    elif mode=='get' and os.path.isfile(q):
        set_last()
        return True
    else:
        set_last(FILE_NOT_FOUND)
        return False
    set_last()
    return True
def check_access(file):
    can_access=ACCESS[ACCESS_VALUE[NOW_USER.access]:]
    if file not in ACCESS:
        set_last(FILE_NOT_FOUND)
        return False
    if file not in can_access:
        set_last(ACCESS_DENIED)
        return False
    set_last()
    return True
def access_file(cmd,file):
    global START_CLOCK,NOW_USER,LAST_USER
    file_=file[0].split('-')
    nowdir=os.getcwd()+'/CH3_Reference_Library/'
    if START_CLOCK>0:
        START_CLOCK-=1
    else:
        if LAST_USER.access:
            NOW_USER=LAST_USER
            LAST_USER=User('','','')
            set_last()
            return 'TIME OUT'
    if cmd=='get':
        if not check_access(file_[0]):return False
        ret=check_file(file_)
        if get_last()!=3 or isinstance(ret,str):return ret
        f=open(nowdir+'/'.join(file_))
        ret=f.read()
        f.close()
        set_last(ACCESS_GRANTED)
        return ret
    if cmd=='updata':
        if not check_access(file_[0]):return False
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
        f.write(file[1])
        f.close()
        set_last(ACCESS_GRANTED)
        return ret
    if cmd=='su':
        if len(file)<2:
            set_last(RUNTIME_ERROR)
            return False
        r=checknum(file[0],User(*(file[1].split('$'))),NOW_USER)
        if r:
            ret=':'.join(r[0:5])+' '+r[7]+' gave '+r[9]+'\n'
            START_CLOCK=int(r)
            LAST_USER=NOW_USER.copy()
            NOW_USER=User(*(file[1].split('$')))
        else:
            return False
        return ret+'Ok,check success,you now access is:'+r[-2]
    if cmd=='gene':
        if len(file)>3:
            set_last(RUNTIME_ERROR)
            return False
        return 'gene a access num:\n'+genenum(NOW_USER,User(*(file[0].split('$'))),file[1],file[2])
def check_ret(ret):
    global NOW_USER
    r=''
    if get_last()!=3:
        r='Unknow Error\n'
        if get_last()==ACCESS_DENIED:
            log('warning',NOW_USER.name+' access denied')
            r='Access Denied\n'
        elif get_last()==ACCESS_GRANTED:
            log('warning',NOW_USER.name+' access granted')
            r='Access Granted\n'
        elif get_last()==FILE_NOT_FOUND:
            log('warning',NOW_USER.name+' access file not found')
            r='File Not Found\n'
        elif get_last()==RUNTIME_ERROR:
            log('error',NOW_USER.name+' Run Time Error!')
            r='Run Time Error\n'
        elif get_last()==FILE_EXISTS_ERROR:
            log('error',NOW_USER.name+' File Exists Error!')
            r='File Exists Error\n'
        elif get_last()==CHECK_FAILED:
            log('warning',NOW_USER.name+' Check failed!')
            r='Check Failed\n'
        else:
            pass
        set_last()
    if isinstance(ret,bool) or not ret:ret=''
    return r+ret
def recv(conn,rsa):
    ms=conn.recv(2048).decode('utf-8').strip()
    return rsa.decode(ms)
def send(conn,rsa,msg):
    ec=rsa.encode(msg)
    conn.send(ec.encode('utf-8'))
def handle(conn,ht):
    global access_list,NOW_USER,LAST_USER,START_CLOCK
    log('info',ht[0]+' connect.')
    #RSA init
    rde=RSA()
    rde.init_de()
    conn.send((str(rde.n)+'|'+str(rde.e)).encode('utf-8'))
    ren=RSA()
    ms=conn.recv(1024).decode('utf-8').strip().split('|')
    if not ms or len(ms)==1:
        conn.send(b'\nLOGIN FAILED.SHUTDOWN HANDLE')
        conn.close()
        log('warning',ht[0]+' send data struct can\'t handle')
        return False
    #struct:N|E
    ren.init_en(ms[1],ms[0])
    ms=recv(conn,rde).strip().split('$')
    if len(ms)==1:
        send(conn,ren,'LOGIN FAILED.SHUTDOWN HANDLE')
        conn.close()
        log('warning',ht[0]+' send data struct can\'t handle')
        return False
    if ms[0] not in access_list or not access_list[ms[0]].login(ms[1]):
        send(conn,ren,'LOGIN FAILED.SHUTDOWN HANDLE')
        conn.close()
        log('warning',ht[0]+' use '+ms[0]+' '+ms[1]+' login Failed')
        return False
    send(conn,ren,'LOGIN SUCCESS')
    log('info',ht[0]+' login success')
    user=access_list[ms[0]]
    NOW_USER=user
    while True:
        strs=recv(conn,rde).strip()
        if strs=='BYEBYE':
            conn.send(b'GOODBYE')
            log('info',NOW_USER.name+' deconnect.')
            conn.close()
            return True
        else:
            command=strs.split()
            if command:
                strip_list(command)
                if len(command)==1:
                    pass
                    #if command[0]=='debug':conn.send(' '.join((str(LAST_USER),str(NOW_USER),str(START_CLOCK))).encode('utf-8'))
                elif len(command)>=2:
                    r=check_ret(access_file(command[0],command[1:]))
                    send(conn,ren,r)
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
    # print(checknum(genenum(User('swwm','deepcloud','root'),User('bbll','','A')),User('swwm','deepcloud','root'),User('bbll','','A')))
    loop()
    
    
    