from random import randint
from math import gcd
from itertools import product

p = 1000003
q = 2001911
n = p * q  # 计算两个大素数的乘积，作为模数n

seed = randint(1, 10)  # 随机选择一个种子值

# 确保选定的随机种子与n互质（最大公约数为1）
while gcd(seed, n) != 1: 
    seed = randint(1, 10)

bits = str(seed % 2)  # 计算初始种子的最低有效位，并转换为字符串
for _ in range(1, 10000):
    seed = (seed * seed) % n  # 使用平方取模算法更新种子
    bit = seed % 2  # 计算新种子的最低有效位
    bits += str(bit)  # 将新计算的位连接到位串上

# 1) 计算长度为1000的子序列中0的平均数量
summation = 0
count = 0
for i in range(len(bits) - 1000):
    for j in range(i, i + 999):
        summation += bits[j].count("0")  # 统计子序列中0的数量
    count += 1
average = summation / count
print("The average number of zeros per subsequence: ", average)
print()

# 计算长度为4的所有可能子序列
subseqFour = [''.join(nums) for nums in product('01', repeat=4)]
freq = {}  # 存储长度为4的子序列频率的字典
for subseq in subseqFour:
    freq[subseq] = 0

# 2) 统计长度为4的子序列出现的频率
for i in range(len(bits) - 4):
    freq[bits[i:i + 4]] += 1  

print("Frequency of length 4 subsequences:")
print("{:<12} {:<8}".format('Subsequence', 'Count'))
for subseq in freq:
    print("{:<12} {:<8}".format(subseq, freq[subseq]))
