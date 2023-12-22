import math
import random

# 定义一个函数来找到一个数的所有质因数
def prime_factors(n):
    factors = []  # 存储质因数的列表
    # 首先处理所有的2，使n成为奇数
    while n % 2 == 0: 
        factors.append(2) 
        n = n / 2
           
    # 检查所有可能的奇数因数，直到sqrt(n)
    for i in range(3, int(math.sqrt(n)) + 1, 2):  
        while n % i == 0: 
            factors.append(i) 
            n = n / i 
    
    # 如果n大于2，那么n本身是一个质数
    if n > 2: 
        factors.append(n)

    return factors

# 定义一个函数来判断a是否可以被b的所有质因数整除
def divisibile(a, b):
    factors = prime_factors(b)  # 获取b的质因数列表

    for i in factors:
        if a % i != 0:
            return False

    return True

# 线性同余生成器（Linear Congruential Generator，LCG）
def lcg(x0, a, c, m):
    full = False  # 用于标记周期是否为完整的m
    # 检查LCG的全周期条件
    if math.gcd(c, m) == 1 and divisibile(a - 1, m) and ((m % 4 == 0) and ((a - 1) % m == 0)):
        full = True
    
    prandomnums = [0] * m  # 初始化随机数数组
    prandomnums[0] = x0  # 设置初始值
    print(prandomnums[0], end=" ")
    # 生成随机数序列
    for i in range(1, m):
        prandomnums[i] = ((prandomnums[i - 1] * a) + c) % m
        print(prandomnums[i], end=" ")
    
    count = 1  # 计数器，用于计算周期长度
    # 判断周期长度
    if full:
        count = m
    else:
        for i in range(1, m):
            if prandomnums[i] != x0:
                count += 1
            else:
                break
    
    print('\nCycle Length: ', count)

# 主函数
if __name__ == '__main__':
    print("Xi = (a*X_i-1 + c)mod m")
    a = int(input('Enter multiplier \'a\': '))  
    c = int(input('Enter increment \'c\': '))  
    m = int(input('Enter modulus param \'m\': '))  
    x0 = random.randint(0, m - 1)  # 随机生成初始值
   
    if m < 0 or a >= m or a <= 0 or c >= m or c < 0:
        print('Wrong Input, Please Follow the constraints')
    else:
        lcg(x0, a, c, m)  # 调用线性同余生成器