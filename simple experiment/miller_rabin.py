import numpy as np

# 随机数生成函数，用于测试中选择随机数a;随机性在算法中扮演着重要角色，它是非确定性测试中的关键。我们的代码使用numpy库的randint函数，通过get_random这一函数接口来产生一个随机整数。在米勒-拉宾检验中，我们需要这个随机数来作为基数，用以执行一系列的测试。
def get_random(i, j=None):
    if j == None:
        # 如果没有提供j，则返回0到i的随机整数
        return np.random.randint(i + 1)
    if i > j:
        # 确保i小于j
        i, j = j, i
    # 返回i到j的随机整数
    return np.random.randint(i, j + 1)

# 快速幂算法，计算(base^power) % n的值;快速幂算法，这是数论中的一个基础工具。我们的fast_power函数就是这一算法的实现。它能够高效地计算base的power次幂模n的结果，这在后续的素性检验中至关重要，因为直接计算大数的幂非常耗时，而快速幂算法则能大幅度优化这一过程。
def fast_power(base, power, n):
    result = 1
    tmp = base
    while power > 0:
        if power & 1 == 1:
            result = (result * tmp) % n
        tmp = (tmp * tmp) % n
        power = power >> 1
    return result

# 米勒-拉宾素性测试函数;首先排除了一些简单情况：如果n是2，则它是素数；如果n是偶数或小于2，它不是素数
def Miller_Rabin(n, s):
    if n == 2:
        # 如果n是2，则直接返回True（2是素数）
        return True
    if n & 1 == 0 or n < 2:
        # 如果n是偶数或小于2，则返回False（不是素数）
        return False
    
    # 它先将n-1分解为2^r * d的形式，这里r是奇数。为什么这么做呢？因为这是寻找所谓的"证人"来证明n的合数性的关键一步。如果n是一个合数，那么这些证人会以很大概率存在。
    m, p = n - 1, 0
    while m & 1 == 0:
        m = m >> 1
        p += 1

    # 进行s次测试;在接下来的检验中，我们多次随机选择一个数a，并计算a^m mod n。如果这个数不是1或n-1，我们继续检查它的平方是否能得到n-1。如果在任何点上我们得到了n-1，那么n可能是一个素数；如果我们没有，那么我们可以几乎肯定n不是素数。
    for _ in range(s):
        # 随机选择一个数a
        a = fast_power(get_random(2, n - 1), m, n)
        if a == 1 or a == n - 1:
            continue
        for __ in range(p - 1):
            a = fast_power(a, 2, n)
            if a == n - 1:
                break
        else:
            # 如果没有找到n-1，则n不是素数
            return False
    # 所有测试都没有证明n是合数，则返回True（n很可能是素数）;这个检验会进行s次，每次选择不同的随机数a。如果在所有这些测试中，我们没有发现n是合数的证据，那么我们可以宣称n是一个素数，尽管如此，这是一个概率性的结论，而不是绝对的。
    return True

if __name__ == '__main__':
    num = 10000
    s = 3
    # 生成小于num的素数列表
    prime = [x for x in range(2, num) if not [y for y in range(2, int(np.sqrt(x) + 1)) if x % y == 0]]
    result = []
    for i in range(num):
        flag = Miller_Rabin(i, s)
        # 验证米勒-拉宾测试结果与已知素数列表是否一致;脚本执行了一个实验，它生成了一个素数列表，并对一系列数值使用米勒-拉宾检验。

        #如果Miller_Rabin函数认为i是素数（flag为真），但i实际上不在通过传统方法得到的素数列表prime中，这意味着Miller_Rabin函数错误地将一个合数判断为素数。这种错误称为"假阳性"，并打印出错误信息和相应的数i。
        if flag and i not in prime:
            print('错误地将一个合数判断为素数: %d' % i)
        #如果Miller_Rabin函数认为i不是素数（flag为假），但i实际上存在于通过传统方法得到的素数列表prime中，这意味着Miller_Rabin函数错误地将一个素数判断为合数。这种错误称为"假阴性"，同样会打印出错误信息和相应的数i
        elif not flag and i in prime:
            print('错误地将一个素数判断为合数: %d' % i)

        #米勒-拉宾素性测试（Miller-Rabin primality test）是一个非确定性的测试，它被设计为一个单向错误算法，这意味着它只会产生第一类错误，也就是假阳性：它可能错误地把一个合数判断为素数，但它不会把一个素数判断为合数