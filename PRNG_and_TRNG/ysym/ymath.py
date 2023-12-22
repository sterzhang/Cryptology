#!/usr/bin/python
# coding:utf-8
from collections import Iterable
import gmpy2
"""
为符号库提供一些基本的数学工具
"""

def is_mpz(obj):
    return True if str(type(obj)) == "<class 'mpz'>" else False

def is_mpfr(obj):
    return True if str(type(obj)) == "<class 'mpfr'>" else False

def gcd(*args):
    """
    计算队列的最大公约数
    传递的数值是整数，非整数将单取整数部分
    """
    def __gcd__(a, b):
        if b == 0:
            return a
        return __gcd__(b, a % b)

    li = []
    for a in args:
        if isinstance(a, Iterable) is True:
            li.extend(a)
        else:
            li.append(a)
    if len(li) == 0:
        return 0
    if len(li) == 1:
        return li[0]

    g = li[0]
    for a in li[1:]:
        g = __gcd__(gmpy2.mpz(g), gmpy2.mpz(a))
    return g


def float_fraction(val, prec=1000):
    """
    浮点数换分数
    返回分数字符串，如果分母为0，则直接返回None表示不得转换
    如果flt是整数，则直接将float转换为int
    如果能返回，则返回两个值，第一个是分子，第二个是分母
    """
    sign = -1 if val < 0 else 1
    flt = abs(val)
    if flt == 0:
        return 0, 1
    f = gmpy2.mpfr(flt) - gmpy2.mpz(flt)
    if f == 0:
        return sign * gmpy2.mpz(flt), 1
    f = gmpy2.mpz(f * prec)
    g = gcd(f, prec)

    # 拥有整数部分
    f_down = gmpy2.mpz(prec) / g
    f_up = f / g
    if gmpy2.mpz(flt) != 0:
        f_up = gmpy2.mpz(flt) * f_down + f_up
        return sign * f_up, f_down
    return sign * f_up, f_down


if __name__ == "__main__":
    pass
else:
    pass
