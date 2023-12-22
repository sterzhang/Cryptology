import math
from ysym.ypolynomial import *
import gmpy2

def is_prime_by_AKS(n):
    """
    使用AKS算法确定n是否是一个素数
    True:n是素数
    False:n是合数
    """

    def __is_integer__(n):
        i = gmpy2.mpz(n)
        f = n - i
        return not f

    def __phi__(n):
        """
        欧拉函数，测试小于n并与n互素的个数
        """
        res = gmpy2.mpz(n)
        a = gmpy2.mpz(n)
        for i in range(2, a+1):
            if a % i == 0:
                res = res // i * (i - 1)
                while a % i == 0:
                    a //= i
        if a > 1:
            res = res // a * (a - 1)
        return res

    # 计算a,b的最大公约数
    def __gcd__(a, b):
        if b == 0:
            return a
        return __gcd__(gmpy2.mpz(b), gmpy2.mpz(a) % gmpy2.mpz(b))
    

    # 1. 确定n是否是纯次幂
    for b in range(2, gmpy2.mpz(gmpy2.floor(gmpy2.log2(n)))+1):
        a = n**(1/b)
        if __is_integer__(a):
            return False

    # 2. 找到一个最小的r，符合o_r(n) > (logn)^2
    maxk = gmpy2.mpz(gmpy2.floor(gmpy2.log2(n)**2))
    maxr = max(3, gmpy2.mpz(gmpy2.ceil(gmpy2.log2(n)**5)))
    nextR = True
    r = 0
    for r in range(2, maxr):
        if nextR == False:
            break
        nextR = False
        for k in range(1, maxk+1):
            if nextR == True:
                break
            nextR = (gmpy2.mpz(n**k % r) == 0) or (gmpy2.mpz(n**k % r) == 1)
    r = r - 1 # 循环多增加了一层
    print("r = %d" % r)

    # 3. 如果存在a<=r 使得 gcd(a,n) != 1 or n，那么返回“合数”
    for a in range(r, 1, -1):
        g = __gcd__(a, n)
        if g > 1 and g < n:
            return False

    # 4. 如果n<= r，输出素数
    if n <= r:
        return True

    # 5. 对于a ∈[1，根号下φ(r)乘以log n]，判断(X+a)^n = (X^n +a)(mod X^r  - 1 , n)是否恒成立。如果不是，那么返回“合数”
    
    # 构造P = (X+a)^n mod (X^r-1)
    # 构造多项式(X+a)^n,并且进行二项式展开
    X = multi_ysymbols('X')
    a = multi_ysymbols('a')
    X_a_n_expand = binomial_expand(ypolynomial1(X, a), n)
    print(X_a_n_expand)
    X.pow(r)
    reduce_poly = ypolynomial1(X, ysymbol(value=-1.0))
    print("构造消减多项式 %s" % reduce_poly)
    print("进行运算 (X+a)^%d mod (X^%d-1)" % (n, r))
    r_equ = ypolynomial_mod(X_a_n_expand, reduce_poly)
    print("得到余式: %s" % r_equ)
    print("进行运算'余式' mod %d 得到式(A)" % n)
    A = ypolynomial_reduce(r_equ, n)
    print("A = %s" % A)
    print("B = x^%d+a mod x^%d-1" % (n, r))
    B = ypolynomial1(multi_ysymbols('X', power=31), a)
    B = ypolynomial_mod(B, reduce_poly)
    print("B = %s" % B)
    C = ypolynomial_sub(A, B)
    print("C = A - B = %s" % C)
    maxa = math.floor(math.sqrt(__phi__(r)) * math.log2(n))
    print("遍历a = 1 to %d" % maxa)
    print("检查每个'%s = 0 (mod %d)'" % (C, n))
    for a in range(1, maxa+1):
        print("检查a = %d" % a)
        C.set_variables_value(a=a)
        v = C.eval()
        if v % n != 0:
            return False

    # 6. 返回“质数”
    return True

if __name__ == "__main__":
    n = 53
    print("检查'%d'是否为素数" % n)
    result = is_prime_by_AKS(n)
    if result is True:
        print("YES")
    else:
        print("NO")
else:
    pass