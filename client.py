# server test client
import socket,sys
import RSA,twoFish
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
if len(sys.argv)<3:
    print('[-] Error!')
    sys.exit(1)
try:
    s.connect((sys.argv[1],int(sys.argv[2])))
    conn=s
    print('[+]','Connect done at %s:%s' %(sys.argv[1],sys.argv[2]))
    ht=(sys.argv[1],sys.argv[2])
    rde=RSA.RSA()
    rde.init_de()
    print('[+]','RSA init done')
    conn.send((str(rde.n)+'|'+str(rde.e)).encode())
    print('[+]','Send RSA public key done')
    rv=conn.recv(1024).decode()
    print('[+]','Get encode key,decoding...')
    tf=twoFish.TwoFish(rde.decode(rv))
    print('[+]','Decode complete.')
    while True:
        sstr=str(input(ht[0] + '>'))
        conn.send(tf.encode(sstr.encode()))
        sstr=tf.decode(conn.recv(102400)).decode().strip()
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