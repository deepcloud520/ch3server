from twofish import Twofish
import secrets
def _16fillblock(strs):
    fb=strs+(16-len(strs)%16)*b' '
    return [fb[i*16:(i+1)*16] for i in range(len(fb)//16)]
class TwoFish:
    def __init__(self,key=None):
        if key is None:self.key=secrets.token_bytes(16)
        else:self.key=key
        self.tf=Twofish(self.key)
    def encode(self,strs):
        strs=_16fillblock(strs)
        ret=b''
        for i in range(len(strs)):
            ret+=self.tf.encrypt(strs[i])
        return ret
    def decode(self,strs):
        strs=_16fillblock(strs)
        ret=b''
        for i in range(len(strs)):
            ret+=self.tf.decrypt(strs[i])
        return ret[:len(ret)-16]
        
    