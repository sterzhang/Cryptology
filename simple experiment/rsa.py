# 1. 随意选择两个大的质数p和q，p不等于q，计算N=pq。
# 2. 根据欧拉函数，不大于N且与N互质的整数个数为(p-1)(q-1)。
# 3. 选择一个整数e与(p-1)(q-1)互质，并且e小于(p-1)(q-1)。
# 4. 用以下这个公式d × e ≡ 1 (mod (p-1)(q-1))计算d。
# 5. 将p和q的记录销毁。

# (N,e)是公钥，(N,d)是私钥。


# 定义求一定范围内的素数的函数
def range_prime(start, end):
    l = list()
    for i in range(start, end+1):
        flag = True
        for j in range(2, i):
            if i % j == 0:
                flag = False
                break
        if flag:
            l.append(i)
    return l

# 定义生成公钥和私钥的函数
def generate_keys(p, q):
    numbers = range_prime(10, 100)  # 在给定范围内生成素数列表
    N = p * q  # 计算N，N是公钥和私钥的一部分,随意选择两个大的质数p和q，p不等于q，计算N=pq。
    C = (p-1) * (q-1)  # 根据欧拉函数计算(p-1)(q-1)。根据欧拉函数，不大于N且与N互质的整数个数为(p-1)(q-1)
    e = 0
    # 选择一个与C互质的e，且e小于C；选择一个整数e与(p-1)(q-1)互质，并且e小于(p-1)(q-1)
    for n in numbers:
        if n < C and C % n > 0:
            e = n
            break
    if e == 0:
        raise Exception("d not found") # 如果没有找到合适的e，则抛出异常

    d = 0
    # 计算d，d是e的模逆，即(d * e) % C == 1；用以下这个公式计算d：d × e ≡ 1 (mod (p-1)(q-1))
    for n in range(2, C):
        if (e * n) % C == 1:
            d = n
            break
    if d == 0:
        raise Exception("d not found") # 如果没有找到合适的d，则抛出异常
    return ((N, e), (N, d))  # 返回公钥(N,e)和私钥(N,d)

# 定义加密函数
def encrypt(m, key):
    C, x = key
    return (m ** x) % C  # 使用公钥key来加密消息m

# 解密函数与加密函数相同，只是使用私钥进行解密
decrypt = encrypt

# 主函数
if __name__ == '__main__':
    pub, pri = generate_keys(47, 79)  # 随机选择两个质数p和q来生成公钥和私钥
    L = list(range(20, 30))  # 创建一个要加密的消息列表
    C = list(map(lambda x: encrypt(x, pub), L))  # 使用公钥加密每条消息
    D = list(map(lambda x: decrypt(x, pri), C))  # 使用私钥解密每条消息
    print("keys:", pub, pri)  # 打印公钥和私钥
    print("message:", L)  # 打印原始消息
    print("encrypt:", C)  # 打印加密后的消息
    print("decrypt:", D)  # 打印解密后的消息
