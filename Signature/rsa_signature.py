#欧几里德迭代求逆算法
def Euclidean(a, p):
    u = a
    v = p
    x1 = 1
    x2 = 0
    while(u != 1):
        q = v//u
        r = v - q * u
        x = x2 - q * x1
        v = u
        u = r
        x2 = x1
        x1 = x
    return x1 % p


# 快速幂算法
def fast_expmod(a,b,n):
    d = 1
    while b != 0:
        if(b & 1) == 1:
            d = (d * a) % n
        b >>= 1
        a = a * a % n
    return d

#生成公私钥
def make_key(p, q, e):
    n = p * q
    phi = (p-1) * (q-1)
    print('phi:\n',hex(phi))
    d = Euclidean(e, phi)     # 辗转相除法求逆(广义欧几里得)
    print('d:\n',hex(d))
    return [[n, e], [n, d]]

#RSA加密
def encrypt(key, plaintext):
    n, e = key
    ciphertext = fast_expmod(plaintext, e, n)
    return ciphertext

#RSA解密
def decrypt(key, ciphertext):
    n, d = key
    plaintext = fast_expmod(ciphertext, d, n)
    return plaintext


if __name__ == '__main__':
    p = 0xE86C7F16FD24818FFC502409D33A83C2A2A07FDFE971EB52DE97A3DE092980279EA29E32F378F5E6B7AB1049BB9E8C5EAE84DBF2847EB94FF14C1E84CF568415
    q = 0xD7D9D94071FCC67EDE82084BBEDEAE1AAF765917B6877F3193BBAEB5F9F36007127C9AA98D436A80B3CCE3FCD56D57C4103FB18F1819D5C238A49B0985FE7B49
    e = 5
    # 获取数据
    plaintext = 0xB503BE7137293906649E0AE436E29819EA2D06ABF31E10091A7383349DE84C5B
    print("明文：\n", hex(plaintext))
    # 公钥、私钥
    public_key, private_key = make_key(p, q, e)
    # 签名
    signature = decrypt(private_key, plaintext)
    print("签名：\n", hex(signature))
    # 验证签名
    plaintext = encrypt(public_key, signature)
    print("验证签名：\n",hex(plaintext))



