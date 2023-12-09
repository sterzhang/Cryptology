"""
SM3是中华人民共和国政府采用的一种密码散列函数标准，适用于商用密码应用中的数字签名和验证、消息认证码的生成与验证以及随机数的生成， 可满足多种密码应用的安全需求
对长度为l(l < 2 ^ 64)
比特的消息m，SM3杂凑算法经过填充和迭代压缩，生成杂凑值，杂凑值长度
为256比特。

s2m2b(s)		字符串s 转化为二进制字符串m & 数据m填充,分组b[i]
cf(v,b)			CF函数实现
zy(n,k)				#循环左移k%32位,共32比特
cut_text(text,lenth)  #数据按间距分组

异或等基础运算
FF(x,y,z,j)
GG(x,y,z,j)
p0(x)
p1(x)
"""
import re
def cut_text(text,lenth):  #数据按间距分组划分iv向量
    textArr = re.findall('.{'+str(lenth)+'}', text)
    textArr.append(text[(len(textArr)*lenth):])
    return textArr
def zy(n,k):        #循环左移k位,共32比特
    k=k%32
    b=str(bin(n))
    b=b.split('0b')[1]
    b=(32-len(b))*'0'+b
    return int(b[k:]+b[:k],2)

def s2m2b(s):               #字符串s 转化为二进制字符串m & 数据m填充,分组b[i]
    r = ""
    x = ""
    for i in s:
        l = 8 - len((x + bin(ord(i))).split('0b')[1]) % 8
        r = r + l * '0' + (x + bin(ord(i))).split('0b')[1]
    k=512-(64+(len(r)+1))%512
    out=r+'1'+k*'0'
    length=bin(len(r)).split('0b')[1]
    t=64-len(length)
    out=out+t*'0'+length
    out=cut_text(out,512)
    return out
def T(j):
    if j<16:
        T =int('0x79cc4519',16)
    else:
        T =int('0x7a879d8a',16)
    return T
def FF(x,y,z,j):  #布尔函数1，式中X,Y,Z 为字。
    if j<=15:
        return x^y^z
    else:
        return (x&y)|(y&z)|(x&z)
def GG(x,y,z,j):    #布尔函数2，式中X,Y,Z 为字。
    if j<=15:
        return x^y^z
    else:
        return (x&y)|(~x&z)

def p0(x):  #置换函数1，式中X为字
    return x^(zy(x,9))^(zy(x,17))
def p1(x):  #置换函数2，式中X为字
    return x^(zy(x,15))^(zy(x,23))

def cf(v,b):
    w = cut_text(b, 32)
    w2 = []
    for j in range(16):
        w[j]=int(w[j],2)
    del w[16]
    for j in range(16, 68):
        x = p1(w[j - 16] ^ w[j - 9] ^ zy(w[j - 3] ,15)) ^ zy(w[j - 13] ,7) ^ w[j - 6]
        w.append(x)
    for j in range(64):
        x = w[j] ^ w[j + 4]
        w2.append(x)
    # print("w1,w2",len(w),len(w2))
    # print("w1,w2",w,w2)
    A=cut_text(v,8)
    # print("len(a),a",len(A),A)
    for i in range(8):
        A[i]=int(A[i],16)
    for j in range(64):
        ss1=zy((zy(A[0],12)+A[4]+zy(T(j),j))%(2**32),7)%(2**32)
        ss2=(ss1^zy(A[0],12))%(2**32)
        tt1=(FF(A[0],A[1],A[2],j)+A[3]+ss2+w2[j])%(2**32)
        tt2=(GG(A[4],A[5],A[6],j)+A[7]+ss1+w[j])%(2**32)
        A[3]=A[2]
        A[2]=zy(A[1],9)
        A[1]=A[0]
        A[0]=tt1
        A[7]=A[6]
        A[6]=zy(A[5],19)
        A[5]=A[4]
        A[4]=p0(tt2)
        # {print(j,end=":")
        # for i in A:
        #     if i !='':
        #         print(hex(i),end=',')
        # print()}
    a=''
    for i in range(8):
        A[i]=str(hex(A[i])).split('0x')[1]
        k=8-len(A[i])
        a=a+k*'0'+A[i]
    v1=int(a,16)^int(v,16)
    v1=hex(v1).split('0x')[1]
    if len(v1)<64:
        v1="0"*(64-len(v1))+str(v1)
    # print(v1,"v1")
    return v1

def G_hash(P):
    # 对明文 hash
    iv = '7380166f4914b2b9172442d7da8a0600a96f30bc163138aae38dee4db0fb0e4e'
    B = s2m2b(P)
    for b in B:
        if b != '':
            iv = cf(iv, b)
    return iv

if __name__ ==  '__main__':
    iv='7380166f4914b2b9172442d7da8a0600a96f30bc163138aae38dee4db0fb0e4e'
    plain = input("请输入明文：")

    B=s2m2b(plain)
    for b in B:
        if b!='':
            iv=cf(iv,b)
    print(iv)


