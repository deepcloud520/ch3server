import socket,sys
import RSA
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
try:
    s.connect((sys.argv[1],int(sys.argv[2])))
    conn=s
    print('connect done at %s:%s' %(sys.argv[1],sys.argv[2]))
    ht=(sys.argv[1],sys.argv[2])
    rde=RSA.RSA()
    rde.init_de()
    conn.send((str(rde.n)+'|'+str(rde.e)).encode('utf-8'))
    ren=RSA.RSA()
    ms=conn.recv(1024).decode('utf-8').strip().split('|')
    ren.init_en(ms[1],ms[0])
    while True:
        sstr=str(input(ht[0] + '>'))
        conn.send(ren.encode(sstr).encode('utf-8'))
        sstr=rde.decode(conn.recv(102400).decode('utf-8')).strip()
        if sstr=='GOODBYE':
            conn.close()
            break
        print(sstr)
except ConnectionRefusedError:
    print('connect to %s:%s failed.' % (sys.argv[1],sys.argv[2]))
except KeyboardInterrupt:
    pass
except BrokenPipeError:
    print('broken pipe.')
finally:
    s.close()