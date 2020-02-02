import random as r
import base64
def gcd(n1,n2):
    """greatest common divisor function """
    return gcd(n2, n1 % n2) if n2 > 0 else n1
def lcm(n1,n2):
    """lowest common multiple function"""
    return n1 * n2 // gcd(n1, n2)
def isz(num):
    if num%2==0:return False
    if num<=3:return True
    for i in range(3,num//2+1,2):
        if num%i==0:return False
    return True
def gene_z(min_,max_):
    n=r.randint(min_,max_)
    while not isz(n):n=r.randint(min_,max_)
    return n

class RSA:
    def init_de(self):
        self.p=gene_z(100,200)
        self.q=gene_z(100,200)
        self.n=self.q*self.p
        ol=(self.q-1)*(self.p-1)
        n=r.randint(1,ol)
        while gcd(n,ol)!=1:n=r.randint(1,ol)
        self.e=n
        d=2
        while (self.e*d)%ol!=1:d+=1
        self.d=d
    def init_en(self,e,n):
        self.e=int(e)
        self.n=int(n)
        self.d=0
    def encode(self,strs):
        if not self.e:
            return False
        strs=base64.b64encode(strs.encode('utf-8')).decode('utf-8')
        ret=''
        for bit in strs:
            asc=ord(bit)
            ret+=chr(asc**self.e%self.n)
        return ret
    def decode(self,strs):
        if not self.d:
            return False
        ret=''
        for bit in strs:
            asc=ord(bit)
            ret+=chr(asc**self.d%self.n)
        return base64.b64decode(ret).decode('utf-8')
if __name__=='__main__':
    print('RSA encode-decode')
    s=int(input('run mode:(encode:1,decode:0)>'))
    if s:
        rsa=RSA()
        n,e=input('plesae input public key(n,e)(use space split)>').split()
        rsa.init_en(e,n)
        print('encode while is start,press ctrl+c to break')
        while True:
            try:
                s=input('>')
                print(rsa.encode(s))
            except KeyboardInterrupt:
                break
    else:
        rsa=RSA()
        rsa.init_de()
        print('Key info:\n','N:',rsa.n,' D:',rsa.d,' E:',rsa.e)
        print('decode while is start,press ctrl+c to break')
        while True:
            try:
                s=input('>')
                print(rsa.decode(s))
            except KeyboardInterrupt:
                break