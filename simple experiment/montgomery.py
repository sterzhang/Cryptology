#蒙哥马利乘法是一种在模M下快速执行大整数乘法的方法，广泛用于密码学领域。这种算法对于模数M是奇数时特别有效，能够避免在计算过程中进行昂贵的除法操作。它通过使用辅助的值R来优化计算，其中R是一个大于M的2的幂次，而且R和M是互质的

def egcd(a, b):
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = egcd(b % a, a)
        return (g, x - (b // a) * y, y)

def modinv(a, m):
    g, x, y = egcd(a, m)
    if g != 1:
        raise Exception('Modular inverse does not exist')
    else:
        return x % m

def mon_mul(A, B, M):
    R = 2 ** (M.bit_length())  # R是大于M的最小的2的幂
    R_inv = modinv(R, M)
    R2 = (R * R) % M
    A_bar = (A * R2) % M
    B_bar = (B * R2) % M
    T = (A_bar * B_bar) % M
    m = (T * R_inv) % M
    if m >= M:
        m -= M
    return m

# # 蒙哥马利乘法函数实现
# def mon_mul(A, B, M):
#     B_bin = bin(B)[2:]  # 将乘数B转换为二进制表示;在代码 B_bin = bin(B)[2:] 中，[2:]的作用是去掉这个二进制字符串的前两个字符，即 "0b"，留下纯粹的二进制数字部分。将乘数 B 以二进制的形式展开，这样可以逐位进行运算，从而避免了一次性的大数计算。
#     print("---------")
#     print(B_bin)
#     print("---------")
#     C = 0
#     for a in B_bin[::-1]:  # 从最低位开始遍历B的每一位,遍历 B 的二进制表示的每一位，可以将问题转化为一系列的加法和右移操作
#         if int(a): C += A  # 如果当前位为1，则将A累加到C。这是因为二进制位值为1表示当前位的权重应该被包含在乘法中。
#         if int(bin(C)[-1]): C += M  # 如果C的最低位为1，则将M累加到C。这一步是蒙哥马利约简的核心，它保证了 C 保持在正确的模范围内。
#         C >>= 1  # 然后将C右移一位，相当于除以2，这相当于乘以R^-1
#     if C >= M: C -= M  # 如果C大于等于M，则进行模M减法，以保证结果小于M
#     return C
 
#传统模乘法函数，用于验证结果
def traditional_mod_mul(A, B, M):
    return (A * B) % M

if __name__ == '__main__':
    # 预计算，选择一个大于M的2的幂R
    R = 2**7 # R的选择
    R2 = 2**14 # R平方，用于预计算和加速蒙哥马利域内转换
    
    # 模数M，通常是一个大质数
    # M = 0x8542D69E4C044F18E8B92435BF6FF7DE457283915C45517D722EDB8B08F1DFC3
    M = 0x61
    
    # 待乘的大整数a和b
    # a = 0xE8B92435BF6FF
    a = 46
    # b = 0x5517D722EDB8B
    b = 65
    
    # 转换为蒙哥马利域：计算A=a*R^2 mod M和B=b*R^2 mod M
    A = mon_mul(a, R2, M)  # 将a转换为蒙哥马利域表示
    B = mon_mul(b, R2, M)  # 将b转换为蒙哥马利域表示
    print("B:------")
    print(B)
    print("-----")
    # 蒙哥马利乘法：计算C=A*B mod M
    C = mon_mul(A, B, M)   # 蒙哥马利乘法，在蒙哥马利域内计算A和B的乘积
    
    # 从蒙哥马利域转换回普通整数：计算result=C*R^-1 mod M
    res = mon_mul(C, R, M) # 将乘积C转换回普通整数表示
    
    # 输出结果
    print("(a*b)modM="+'{:x}'.format(res))  # 输出蒙哥马利乘法的结果
    
    # 传统模乘法结果，用于验证
    res_traditional = traditional_mod_mul(a, b, M)
    
    # 输出蒙哥马利乘法结果
    print("(a*b)modM="+'{:x}'.format(res_traditional))
    
    # 验证蒙哥马利乘法结果是否正确
    assert res == res_traditional, "验证失败：蒙哥马利乘法结果与传统模乘法结果不符。"

    # 如果验证通过，打印验证成功的信息
    print("验证成功：蒙哥马利乘法结果与传统模乘法结果相符。")