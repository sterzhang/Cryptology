from bitarray import bitarray
from bitarray.util import int2ba, ba2int, ba2hex
import binascii
import ZUC_components as zuc

# 不丢失位的移位函数
def rol(bits, shift_num):
    return bits[shift_num:] + bits[:shift_num]

# 线性变换L1，L2都是将 32 位的字转换成另一个 32 位的字
def L1(bits):
    return bits ^ rol(bits, 2) ^ rol(bits, 10) ^ rol(bits, 18) ^ rol(bits, 24)

def L2(bits):
    return bits ^ rol(bits, 8) ^ rol(bits, 14) ^ rol(bits, 22) ^ rol(bits, 30)

# 生成S-box
def S(bits):
    result = bitarray('')
    result += int2ba(zuc.s0[ba2int(bits[0:8])], length=8)
    result += int2ba(zuc.s1[ba2int(bits[8:16])], length=8)
    result += int2ba(zuc.s0[ba2int(bits[16:24])], length=8)
    result += int2ba(zuc.s1[ba2int(bits[24:32])], length=8)
    return result


class ZUC:
    #整体流程，经历两个阶段，初始化阶段和工作阶段
    def __init__(self, key, iv):
        self.initialize(key, iv)
        self.generate_32bit()
    
    # ZUC算法第一个阶段是初始化：分为1.密钥装入 2.将F中的R1，R2置为0 3.执行32次循环
    def initialize(self, key, iv):
        # 1.密钥装入：将初始密钥key和初始向量iv作为输入，与d进行拼接，得到s0~s15
        self.s = []
        for i in range(16):
            self.s.append(key[i*8:i*8+8] + int2ba(zuc.d[i], length=15) + iv[i*8:i*8+8])
        # 2.将F中的R1，R2置为0
        self.r1 = self.r2 = int2ba(0, length=32)
        # 3.执行32次循环（1.比特重组 2.非线性函数输出W 3.LSFR初始化）
        for i in range(32):
            # 1.比特重组（输出X0，X1，X2，X3）
            self.BitReconstruction()
            # 2.将上一步得到的X0，X1，X2，X3作为输入传给F函数，得到W
            self.F()
            # 3.将上一步得到的W送进LSFR初始化模式得到S0~S15
            self.LFSRWithInitializationMode()
    
    # 比特重组BR：从LFSR中提取出来128bit组成4个32bit的字，前三个字提供给底层非线性F函数使用的，最后一个字用来生成密钥流
    def BitReconstruction(self):
        self.x0 = self.s[15][:16] + self.s[14][-16:]
        self.x1 = self.s[11][-16:] + self.s[9][:16]
        self.x2 = self.s[7][-16:] + self.s[5][:16]
        self.x3 = self.s[2][-16:] + self.s[0][:16]
    
    # 非线性函数F：含有2个32bit的记忆单元R1，R2；输入位3个32bit的字X0，X1，X2，输出32bit的W
    def F(self):
        # W是X0和R1异或后，跟R2进行模2^32加法运算，作为输出W
        self.w = int2ba((ba2int(self.x0 ^ self.r1) + ba2int(self.r2)) % (2**32), length=32)
        # 更新W1，W2
        w1 = int2ba((ba2int(self.r1) + ba2int(self.x1)) % (2**32), length=32)
        w2 = self.r2 ^ self.x2
        # 更新R1，R2
        self.r1 = S(L1(w1[-16:] + w2[:16]))
        self.r2 = S(L2(w2[-16:] + w1[:16]))
        return self.w
    
    # LFSR的初始化模式：读入一个31位的输入字u，通过从非线性函数F的32位输出W中删除最右边的位来获得
    def LFSRWithInitializationMode(self):
        v = (2**15*ba2int(self.s[15]) + 2**17*ba2int(self.s[13]) + 2**21*ba2int(self.s[10]) \
             + 2**20*ba2int(self.s[4]) + (1+2**8)*ba2int(self.s[0])) % (2**31 - 1)
        s16 = int2ba((v + ba2int(self.w[:-1])) % (2**31 - 1), length=31)
        for i in range(15):
            self.s[i] = self.s[i + 1]
        self.s[15] = s16
    
    # LSFR的工作模式：没有输入
    def LFSRWithWorkMode(self):
        s16 = (2**15*ba2int(self.s[15]) + 2**17*ba2int(self.s[13]) + 2**21*ba2int(self.s[10]) \
                + 2**20*ba2int(self.s[4]) + (1+2**8)*ba2int(self.s[0])) % (2**31 - 1)
        if s16 == 0:
            s16 = 2**31 - 1
        s16 = int2ba(s16, length=31)
        # 将(s1,s2...s16)->(s0,s1...s15)
        for i in range(15):
            self.s[i] = self.s[i + 1]
        self.s[15] = s16
    
    # ZUC的第二个阶段 工作模式
    def generate_32bit(self):
        # 1.比特重组：将初始化后的S0~S15进行比特重组，得到X0，X1，X2，X3
        self.BitReconstruction()
        # 2.F函数：工作模式下不需要保留F函数的输出W（将W丢弃），仅仅是对F函数的R0，R1进行更新
        z = self.F() ^ self.x3
        # 3.进入LFSR工作模式
        self.LFSRWithWorkMode()
        return z

def bit2str(bits):
    padBit = (4 - len(bits) % 4) % 4
    return ba2hex(bitarray('0'*padBit) + bits)
    # return ba2hex(bitarray('0'*padBit) + bits).decode()



if __name__ == "__main__":
    # ZUC的输入如下（这里采用书上171页的例子）：
    # 1.初始密钥key
    key = int2ba(0x3d4c4be96a82fdaeb58f641db17b455b, length=128)
    # 2.初始向量iv
    iv = int2ba(0x84319aa8de6915ca1f6bda6bfbd8c766, length=128)
    # 3.正整数L（由明文比特长度/32向上取整得到）
    L = 2

    # 现在进入ZUC算法
    zucBlock = ZUC(key, iv)
    for i in range(L):
        print(bit2str(zucBlock.generate_32bit()))