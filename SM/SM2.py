import random,math,SM3

# 扩展欧几里得算法求逆元
def get_gcd(a, b): 
    if(b==0):          
        return 1,0,a     
    else:         
        x,y,gcd = get_gcd(b,a%b)      
        x,y = y,(x-(a//b)*y)        
        return x,y,gcd

# 两点加法
def add_point(x1,y1,x2,y2,p):
    if(x1=='O' and y1=='O'):
        return x2,y2
    elif(x2=='O' and y2=='O'):
        return x1,y1
    elif(x1==x2 and y2==((-1)*y1)%p):
        x3 = 'O'
        y3 = 'O'
        return x3,y3
    else:
        inv,y,gcd = get_gcd(x2-x1,p)
        lbd = ((y2-y1)*inv)%p
        x3 = (lbd**2-x1-x2)%p
        y3 = (lbd*(x1-x3)-y1)%p
        return x3,y3

# 倍点算法
def multiply2_point(x1,y1,a,p):
    if(x1=='O' and y1=='O'):
        return x1,y1
    else:
        inv,y,gcd = get_gcd(2*y1,p)
        lbd = ((3*(x1**2)+a)*inv)%p
        x3 = (lbd**2-2*x1)%p
        y3 = (lbd*(x1-x3)-y1)%p
        return x3,y3

# k倍点算法
def multiplyk_point(Px,Py,k,a,p):
    k = bin(k)[2:]
    Qx = 'O'
    Qy = 'O'
    for j in range(len(k)):
        Qx,Qy = multiply2_point(Qx,Qy,a,p)
        if(k[j]=='1'):
            Qx,Qy = add_point(Qx,Qy,Px,Py,p)
    return Qx,Qy

# 验证公钥满足条件
def key_statisfy(n,Px,Py,a,b,p):
    # P不能是无穷远点
    if(Px=='O' or Py=='O'):
        return False
    # P必须是Fq中的元素
    if(Px<0 or Py<0 or Px>p-1 or Py>p-1):
        return False
    # P满足椭圆曲线方程
    left = (Py**2)%p
    right = (Px**3+a*Px+b)%p
    if(left!=right):
        return False
    # [n]P为无穷远点
    nPx,nPy = multiplyk_point(Px,Py,n,a,p)
    if(nPx!='O' or nPy!='O'):
        return False
    return True

# 产生公钥
def gen_keypair(n,Gx,Gy,a,b,p):
    d = random.randint(1,n-1)
    Px,Py = multiplyk_point(Gx,Gy,d,a,p)
    while(not key_statisfy(n,Px,Py,a,b,p)):
        d = random.randint(1,n-1)
        Px,Py = multiplyk_point(Gx,Gy,d,a,p)
    return d,Px,Py

# 域元素到比特串的转换
def Fq2bit(alpha,p):
    t = math.ceil(math.log(p,2))
    M = bin(alpha)[2:]
    while(len(M)%8!=0 or len(M)!=t):
        M = '0' + M
    #print(M,len(M))
    return M

# 点到比特串转换
def point2bit(xp,yp,p):
    PC = '00000100'  # 选择不压缩模式
    xp_bit = Fq2bit(xp,p)
    yp_bit = Fq2bit(yp,p)
    return PC+xp_bit+yp_bit

# KDF combined with SM3
def KDF(Z,klen):
    v = 256
    ct = 1
    Ha = {}
    for i in range(1,math.ceil(klen/v)+1):
        Ha[i] = SM3.SM3_digest(Z+bin(ct)[2:].zfill(32))
        ct += 1
    # klen/v is integer
    index = math.ceil(klen/v)
    Haa = ''
    if(math.ceil(klen/v)==klen/v):
        Haa = Ha[index]
    else:
        Haa = Ha[index][:klen-(v*math.floor(klen/v))]
    K = ''
    for i in range(1,math.ceil(klen/v)):
        K += Ha[i]
    K += Haa
    return K

# 按位异或
def Xor(a,b):
    result =''
    if len(a)!=len(b):
        return False
    for i in range(len(a)):
        if a[i]==b[i]:
            result += '0'
        else:
            result += '1'
    return result

# 比特串转域元素
def bit2Fq(b):
    for i in range(len(b)):
        if(b[i]=='1'):
            b=b[i:]
            break
    return int(b,base=2)

# 消息字符串转比特串
def msg2bit(msg):
    res = ''
    for c in msg:
        a = ord(c)
        res += bin(a)[2:].zfill(8)
    return res    

# 比特串转消息字符串
def bit2msg(b):
    res = ''
    for i in range(int(len(b)/8)):
        cbit = b[i*8:(i+1)*8]
        res += chr(int(cbit,base=2))
    return res

# bit str M
def SM2_encrypt(M,n,Gx,Gy,a,b,p,Px,Py):
    #print('SM2 ENCRYPTION')
    klen = len(M)
    # A1. 用随机数发生器产生随机数 k ∈ [1，n-1]
    k = random.randint(1,n-1)

    # A2. 计算椭圆曲线点 C_1=[k]G=(x1，y1),按 GB/T 2918.1-2016 中 4.2.9 和 4.2.5 给出的方法，将 C_1的数据类型转换为比特串;
    x1,y1 = multiplyk_point(Gx,Gy,k,a,p)
    C1 = point2bit(x1,y1,p)

    # A3. 计算椭圆曲线点 S=[h]P_B,若 S 是无穷远点,则报错并退出
    h = math.floor(((math.sqrt(p)+1)**2)/n)
    Sx,Sy = multiplyk_point(Px,Py,h,a,p)
    if(Sx=='O' or Sy=='0'):
        return False
    
    # A4. 计算椭圆曲线点[k]P_B=(x2，y2),按 GB/T 32918.1-2016 中 4.2.6 和 4.2.5 给出的方法,将坐标 x2、y2的数据类型转换为比特串
    x2,y2 = multiplyk_point(Px,Py,k,a,p)
    x2_bit = Fq2bit(x2,p)
    y2_bit = Fq2bit(y2,p)

    # A5. 计算 t=KDF(x_2 || y_2,klen),若 t 为全 0 比特串,则返回 A_1
    t = KDF(x2_bit+y2_bit,klen)
    if(int(t,base=2)==0):
        return False
    
    # A6. 计算 C_2
    C2 = Xor(M,t)

    # A7. 计算C_3
    C3 = SM3.SM3_digest(x2_bit+M+y2_bit)

    # A8. 输出密文C
    C = [C1,C2,C3]
    return C 

def SM2_decrypt(C,n,Gx,Gy,a,b,p,d):
    #print('SM2 DECRYPTION')
    C1 = C[0]
    C2 = C[1]
    C3 = C[2]
    klen = len(C2)
    # B1
    PC = C1[:8] # PC=04
    bit_len = int((len(C1)-8)/2)
    x1 = bit2Fq(C1[8:8+bit_len])
    y1 = bit2Fq(C1[8+bit_len:])
    left = (y1**2)%p
    right = (x1**3+a*x1+b)%p
    if(left!=right):
        return False
    # B2
    h = math.floor(((math.sqrt(p)+1)**2)/n)
    Sx,Sy = multiplyk_point(Px,Py,h,a,p)
    if(Sx=='O' or Sy=='0'):
        return False
    # B3
    x2,y2 = multiplyk_point(x1,y1,d,a,p)
    x2_bit = Fq2bit(x2,p)
    y2_bit = Fq2bit(y2,p)
    # B4
    t = KDF(x2_bit+y2_bit,klen)
    if(int(t,base=2)==0):
        return False
    # B5
    MM = Xor(C2,t)
    # B6
    u = SM3.SM3_digest(x2_bit+MM+y2_bit)
    if(u!=C3):
        return False
    # B7
    return MM

if __name__ == "__main__":
    
    # y^2=x^3+ax+b
    # 推荐系统参数
    p=int('FFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFF',base=16)
    a=int('FFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFC',base=16)
    b=int('28E9FA9E9D9F5E344D5A9E4BCF6509A7F39789F515AB8F92DDBCBD414D940E93',base=16)
    n=int('FFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFF7203DF6B21C6052B53BBF40939D54123',base=16)
    Gx=int('32C4AE2C1F1981195F9904466A39C9948FE30BBFF2660BE1715A4589334C74C7',base=16)
    Gy=int('BC3736A2F4F6779C59BDCEE36B692153D0A9877CC62A474002DF32E52139F0A0',base=16)
    # p=int('17',base=16)
    # a=int('1',base=16)
    # b=int('1',base=16)
    # n=int('FFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFF7203DF6B21C6052B53BBF40939D54123',base=16)
    # Gx=int('32C4AE2C1F1981195F9904466A39C9948FE30BBFF2660BE1715A4589334C74C7',base=16)
    # Gy=int('BC3736A2F4F6779C59BDCEE36B692153D0A9877CC62A474002DF32E52139F0A0',base=16)
    # 附录实例参数
    '''
    p=int('8542D69E4C044F18E8B92435BF6FF7DE457283915C45517D722EDB8B08F1DFC3',base=16)
    a=int('787968B4FA32C3FD2417842E73BBFEFF2F3C848B6831D7E0EC65228B3937E498',base=16)
    b=int('63E4C6D3B23B0C849CF84241484BFE48F61D59A5B16BA06E6E12D1DA27C5249A',base=16)
    n=int('8542D69E4C044F18E8B92435BF6FF7DD297720630485628D5AE74EE7C32E79B7',base=16)
    Gx=int('421DEBD61B62EAB6746434EBC3CC315E32220B3BADD50BDC4C4E6C147FEDD43D',base=16)
    Gy=int('0680512BCBB42C07D47349D2153B70C4E5D7FDFCBFA36EA1A85841B9E46E09A2',base=16)'''

    # 产生公私钥对
    d,Px,Py = gen_keypair(n,Gx,Gy,a,b,p)
    print('d:',hex(d),'\nPx:',hex(Px),'\nPy:',hex(Py))

    # SM2_Encrpytion
    msg = 'encryption standard'
    print('明文为：',msg)
    plain_text = msg2bit(msg)
    cipher_text = SM2_encrypt(plain_text,n,Gx,Gy,a,b,p,Px,Py)
    hexresult = ''
    for c in cipher_text:
        hexresult += hex(int(c,base=2))
    print('加密得到密文：',hexresult)

    # SM2_Decryption
    decrypt_text = SM2_decrypt(cipher_text,n,Gx,Gy,a,b,p,d)
    decrypt_text = bit2msg(decrypt_text)
    print('解密得到明文：',decrypt_text)