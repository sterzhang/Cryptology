# 按位与运算
def And(a,b):
    result =''
    if len(a)!=len(b):
        print('len(a)!=len(b)')
        return False
    for i in range(len(a)):
        if (a[i]=='1')&(b[i]=='1'):
            result += '1'
        else:
            result += '0'
    return result

# 三变量按位与运算
def And3(a,b,c):
    return And(And(a,b),c)

# 按位或运算
def Or(a,b):
    result =''
    if len(a)!=len(b):
        print('len(a)!=len(b)')
        return False
    for i in range(len(a)):
        if (a[i]=='1')|(b[i]=='1'):
            result += '1'
        else:
            result += '0'
    return result

# 三变量按位或运算
def Or3(a,b,c):
    return Or(Or(a,b),c)

# 按位异或
def Xor(a,b):
    result =''
    if len(a)!=len(b):
        print('len(a)!=len(b)')
        return False
    for i in range(len(a)):
        if a[i]==b[i]:
            result += '0'
        else:
            result += '1'
    return result

# 三变量按位异或运算
def Xor3(a,b,c):
    return Xor(Xor(a,b),c)

# 按位非运算
def Not(a):
    result = ''
    for ch in a:
        if ch == '1':
            result = result + '0'
        else:
            result = result + '1'
    return result

# 模2^32算数加
def Mod32(a,b):
    c = (a + b)
    d = c%(2**32)
    ans = str(d)
    return ans

# 循环左移函数
def LeftRotate(text, num):
    text = str(text)
    return (text[num:] + text[:num])

# 布尔函数FFj
def FF(x,y,z,j):
    if((j>=0)&(j<=15)):
        ans = Xor3(x,y,z)
    else:
        ans = Or3(And(x,y),And(x,z),And(y,z))
    return ans

# 布尔函数GGj
def GG(x,y,z,j):
    if((j>=0)&(j<=15)):
        ans = Xor3(x,y,z)
    else:
        ans = Or(And(x,y),And(Not(x),z))
    return ans

# 置换函数
def P(x, mode):
    if mode == 0:
        ans = Xor3(x,LeftRotate(x,9),LeftRotate(x,17))
    else:
        ans = Xor3(x,LeftRotate(x,15),LeftRotate(x,23))
    return ans

# 填充消息m
def Fill(m):
    # 获得m二进制串
    m_bin = ''
    for ch in m:
        ascii_ch = ord(ch)
        m_bin = m_bin + '0' + bin(ascii_ch)[2:]
    #print(m_bin)
    # 添加1
    length = len(m_bin)
    m_bin = m_bin + '1'

    # 添加k个0
    while len(m_bin)%512!=448:
        m_bin += '0'

    # 为l的二进制表示补齐0
    length_bin = bin(length)[2:]
    while len(length_bin)<64:
        length_bin = '0' + length_bin

    m_bin = m_bin + length_bin
    return m_bin

# 消息扩展
def Expand(Bi):
    w = {}  # Bi划分为132个字
    # 5.3.2 a)
    for i in range(16):
        w[i] = Bi[i*32:(i+1)*32]
    # 5.3.2 b)
    for j in range(16, 68):
        tmp = Xor3(w[j-16],w[j-9],LeftRotate(w[j-3],15))
        tmp = P(tmp, 1)
        w[j] = Xor3(tmp, LeftRotate(w[j-13],7), w[j-6])
    # 5.3.2 c)
    for j in range(64):
        w[j+68] = Xor(w[j],w[j+4])
    for i in w:
        w[i] = ZtoH(w[i])  # 二进制转十六进制
    return w

# 压缩函数
def Compress(w,IV):

    A = IV[0:8]
    B = IV[8:16]
    C = IV[16:24]
    D = IV[24:32]
    E = IV[32:40]
    F = IV[40:48]
    G = IV[48:56]
    H = IV[56:64]
    SS1 = ''
    SS2 = ''
    TT1 = ''
    TT2 = ''
    
    for j in range(64):
        if int(j)<=15:
            T = '79cc4519' 
        else:
            T = '7a879d8a'

        tmp = int(LeftRotate(HtoB(A),12), 2) + int(HtoB(E), 2) + int(LeftRotate(HtoB(T),j%32), 2) 
        tmp = Mod32(tmp, 0)
        SS1 = LeftRotate(OtoB(tmp), 7)
        SS2 = Xor(SS1, LeftRotate(HtoB(A),12))

        tmp = int(FF(HtoB(A),HtoB(B),HtoB(C),j),2) + int(HtoB(D),2) + int(SS2,2) + int(HtoB(w[j+68]),2)
        tmp = Mod32(tmp,0)
        TT1 = int(tmp,10)

        tmp = int(GG(HtoB(E),HtoB(F),HtoB(G),j),2) + int(HtoB(H),2) + int(SS1,2) + int(HtoB(w[j]),2)
        tmp = Mod32(tmp,0)
        TT2 = int(tmp,10)

        D = C
        C = ZtoH(LeftRotate(HtoB(B),9))
        B = A
        A = OtoH(TT1)
        H = G
        G = ZtoH(LeftRotate(HtoB(F),19))
        F = E
        E = ZtoH(P(OtoB(TT2),0))

    r = A+B+C+D+E+F+G+H
    r = HtoB(r)
    v = HtoB(IV)
    return BtoH(Xor(r,v))

# 迭代
def Iteration(m,w):
    IV = {}
    IV[0] = '7380166f4914b2b9172442d7da8a0600a96f30bc163138aae38dee4db0fb0e4e'
    length = len(m)
    n = length//512
    b = {}  # 对消息按512bit分组
    for i in range(n):
        b[i] = m[512*i:512*(i+1)]
        w = Expand(b[i])
        IV[i+1] = Compress(w,IV[i])
    return HtoB(IV[n])

# 2进制转16进制，用于expand函数
def ZtoH(text):
    text = str(text)
    while len(text)<32:
        text = '0' + text
    text_16 = ''
    for i in range(8):
        tmp = hex(int(text[4*i:4*(i+1)],base = 2))[2:]
        text_16 = text_16 + tmp   
    return text_16

# 2进制转16进制
def BtoH(text):
    text = str(text)
    while len(text)<32:
        text = '0' + text
    text_16 = ''
    for i in range(len(text)//4):
        tmp = hex(int(text[4*i:4*(i+1)],base = 2))[2:]
        text_16 = text_16 + tmp
    return text_16

# 16进制转2进制
def HtoB(text):
    text_2 = ''
    text = str(text)
    for ch in text:
        tmp = bin(int(ch ,base = 16))[2:]
        for i in range(4):
            if len(tmp)%4!=0:
                tmp = '0' + tmp
        text_2 = text_2 + tmp   
    while len(text_2)<32:
        text_2 = '0' + text_2      
    return text_2

# 10进制转2进制
def OtoB(text):
    text_10 = ''
    text = str(text)
    tmp = bin(int(text ,base = 10))[2:]
    text_10 = text_10 + tmp  
    while len(text_10)<32:
        text_10 = '0' + text_10      
    return text_10

# 10进制转16进制
def OtoH(text):
    text_10 = ''
    text = str(text)
    tmp = hex(int(text ,base = 10))[2:]
    text_10 = text_10 + tmp     
    while len(text_10)<8:
        text_10 = '0' + text_10   
    return text_10

# SM3_digest
def SM3_digest(c):
    m = Fill(c)
    w = Expand(m)
    b = Iteration(m,w)
    return b

if __name__ == "__main__":
    c = 'cybersecurity' # 要加密的内容
    m = Fill(c)
    #print(m)
    w = Expand(m)
    #print(w)
    b = Iteration(m,w)
    print("plaintext:",c)
    print("digest:",b,len(b))