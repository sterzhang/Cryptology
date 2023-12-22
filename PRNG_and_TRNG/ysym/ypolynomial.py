#!/usr/bin/python
# coding:utf-8
import copy
import math
import gmpy2
from ysym.ymath import *
from ysym.yvalue import *
from ysym.ypolynomial import *


def multi_ysymbols_is_can_add_or_sub(ms1, ms2):
    """
    测试两个multi_ysymbols是否可以相加
    具有相同的指数的变量
    """
    if type(ms1) is not multi_ysymbols or type(ms2) is not multi_ysymbols:
        return False

    if ms1.is_zero() is True or ms2.is_zero() is True:
        return True

    # 变量与指数必须全部相同
    for name in ms2.variables:
        # 只要有任何一个变量不相同则不能相加
        if name not in ms1.variables:
            return False
        # 测试指数必须全部相同
        if ms1.variables[name].power != ms2.variables[name].power:
            return False
    # 两个multi_ysymbols必须有相同数目的变量
    if len(ms1.variables) == len(ms2.variables):
        return True
    return False


def multi_ysymbols_add(ms1, ms2):
    """
    两个multi_ysymbols相加
    必须其中的变量与指数都相同
    """
    if type(ms1) is not multi_ysymbols or type(ms2) is not multi_ysymbols:
        raise TypeError
    if multi_ysymbols_is_can_add_or_sub(ms1, ms2) is False:
        return None
    if ms1.is_zero() is True and ms2.is_zero() is True:
        return multi_ysymbols('0')
    if ms1.is_zero() is True and ms2.is_zero() is False:
        return multi_ysymbols(ms2)
    if ms1.is_zero() is False and ms2.is_zero() is True:
        return multi_ysymbols(ms1)
    result = copy.deepcopy(ms1)
    # 指数一样，变量相同，系数相加即可
    result.set_const_value(yvalue_add(ms1.const.value(), ms2.const.value()))
    return result


def multi_ysymbols_sub(ms1, ms2):
    """
    两个multi_ysymbols相减
    """
    if type(ms1) is not multi_ysymbols or type(ms2) is not multi_ysymbols:
        return None
    if multi_ysymbols_is_can_add_or_sub(ms1, ms2) is False:
        return None
    if ms1.is_zero() is True and ms2.is_zero() is True:
        return multi_ysymbols('0')
    if ms1.is_zero() is True and ms2.is_zero() is False:
        ms3 = copy.deepcopy(ms2)
        ms3.set_const_value(-1 * ms3.const.value())
        return multi_ysymbols(ms3)
    if ms1.is_zero() is False and ms2.is_zero() is True:
        return multi_ysymbols(ms1)
    ms3 = copy.deepcopy(ms2)
    ms3.set_const_value(-1 * ms3.const.value())
    result = multi_ysymbols_add(ms1, ms3)
    return result


def multi_ysymbols_mul(ms1, ms2):
    if type(ms1) is not multi_ysymbols or type(ms2) is not multi_ysymbols:
        raise TypeError
    v1 = copy.deepcopy(ms1)
    v2 = copy.deepcopy(ms2)
    v1.mul(v2)
    return v1


def multi_ysymbols_div(ms1, ms2, diff=False):
    if type(ms1) is not multi_ysymbols or type(ms2) is not multi_ysymbols:
        raise TypeError

    # 除0异常
    if ms2.is_zero() is True:
        raise ZeroDivisionError

    if ms1.is_const() is True and ms2.is_const() is True:
        return multi_ysymbols(yvalue_div(ms1.const.get_value(),
                                         ms2.const.get_value()))
    elif ms1.is_const() is True and ms2.is_const() is False:
        return multi_ysymbols(1)
    elif ms1.is_const() is False and ms2.is_const() is True:
        return multi_ysymbols(1)
    else:
        # 如果在已经存在符号则相减指数，如果不存在则添加变量，指数为负数
        quotient = copy.deepcopy(ms1)
        for var in quotient.variables:
            if var in ms2.variables:
                if quotient.variables[var].power == ms2.variables[var].power:
                    quotient.variables.pop(var)
                elif quotient.variables[var].power > ms2.variables[var].power:
                    quotient.variables[var].power -= ms2.variables[var].power
                else: # quotient.variables[var].power < ms2.variables[var].power
                    quotient.variables[var].power -= ms2.variables[var].power
        # 反向遍历从除数中找被除数中不存在变量
        for var in ms2.variables:
            if var not in ms1:
                quotient.variables[var] = copy.deepcopy(ms2.variables[var])
                quotient.variables[var].power *= -1
    coefficient = yvalue_div(ms1.const.get_value(), ms2.const.get_value())
    quotient.set_const_value(coefficient)
    return quotient


def multi_ysymbols_list_x_loop_single(ms_list, cond=None, doit=None):
    """
    对单个multi_ysymbols列表进行处理
    """
    if type(ms_list) is not list:
        raise TypeError

    if cond is None:
        cond = multi_ysymbols_is_can_add_or_sub
    if doit is None:
        doit = multi_ysymbols_add

    use_it = set()
    result = []
    i = 0
    for ms in ms_list:
        if type(ms) is not multi_ysymbols or i in use_it:
            i += 1
            continue
        r = ms
        use_it.add(i)
        j = 0
        for ms2 in ms_list:
            if type(ms2) is not multi_ysymbols or j in use_it:
                j += 1
                continue
            if cond(ms, ms2) is True:
                r = doit(r, ms2)
                use_it.add(j)
            j += 1
        # 添加到结果列表
        result.append(r)
        i += 1
    # 降序排列
    result = sorted(result, reverse=True)
    return result


def multi_ysymbols_list_x_loop(ms1_list_arg, ms2_list_arg, cond=None, doit=None):
    """
    交叉遍历两个列表
    cond是条件函数，doit是功能函数
    """
    if type(ms1_list_arg) is not list or type(ms2_list_arg) is not list:
        raise TypeError

    if cond is None:
        cond = multi_ysymbols_is_can_add_or_sub
    if doit is None:
        doit = multi_ysymbols_add

    ms1_list = copy.deepcopy(ms1_list_arg)
    ms2_list = copy.deepcopy(ms2_list_arg)

    use_it = set()
    result = []
    r = multi_ysymbols('0')
    i = 0
    while i < len(ms1_list):
        # 非multi_ysymbols则跳过，或者索引在使用列表中
        if type(ms1_list[i]) is not multi_ysymbols:
            i += 1
            continue
        j = 0
        ms1 = ms1_list[i]
        while j < len(ms2_list):
            if type(ms2_list[j]) is not multi_ysymbols:
                j += 1
                continue
            # 如果在不已使用列表中，则进行运算
            if j not in use_it:
                ms2 = ms2_list[j]
                if cond(ms1, ms2) is True:
                    use_it.add(j)
                    ms1 = doit(ms1, ms2)
                    #print("%s + %s = %s" % (ms1, ms2, r))
                    if ms1.is_zero() is True:
                        break
            j += 1
        # 如果经历过一次最终的结果ms1为0则直接进入下一次循环
        if ms1.is_zero() is False:
            result.append(ms1)
        i += 1

    # 将p2_list中没有进行合并的multi_ysymbols录入到result中
    i = 0
    while i < len(ms2_list):
        # 不在使用列表中，并且是multi_ysymbols类型
        if i not in use_it and type(ms2_list[i]) is multi_ysymbols:
            result.append(ms2_list[i])
            #print("append ms2 '%s' to result" % ms2_list[i])
        i += 1
    return result


def multi_ysymbols_list_add(ms1_list, ms2_list):
    """
    两个multi_ysymbols列表相加,同变量同幂的项相加
    如果列表中有非multi_ysymbols的类型，则忽略
    返回一个multi_ysymbols列表
    """
    result = multi_ysymbols_list_x_loop(ms1_list, ms2_list,
                                        multi_ysymbols_is_can_add_or_sub,
                                        multi_ysymbols_add)
    return result


def multi_ysymbols_list_sub(ms1_list, ms2_list):
    """
    两个列表相乘，最后得到一个大的multi_ysymbols
    这里先把减数队列的符号变换然后做加法操作
    """
    ms3_list = copy.deepcopy(ms2_list)
    for ms in ms3_list:
        ms.set_const_value(-1 * ms.const.value())
        #print("ms = %s" % ms)
    result = multi_ysymbols_list_x_loop(ms1_list, ms3_list,
                                        multi_ysymbols_is_can_add_or_sub,
                                        multi_ysymbols_add)
    return result


def multi_ysymbols_list_mul(ms1_list, ms2_list):
    if type(ms1_list) is not list or type(ms2_list) is not list:
        raise TypeError
    result = multi_ysymbols(*ms1_list)
    result.mul(*ms2_list)
    return result


def multi_ysymbols_list_div(ms1_list, ms2_list):
    if type(ms1_list) is not list or type(ms2_list) is not list:
        raise TypeError
    result = multi_ysymbols(*ms1_list)
    for ms in ms2_list:
        result.div(ms)
    return result


def multi_ysymbols_is_zero(ms):
    if type(ms) is multi_ysymbols:
        return ms.is_zero()
    return False


def multi_ysymbols_merge(a1, a2, names=[], strict=0):
    """
    合并同类项
    返回多项式2型
    a1,a2是两个multi_ysymbols

    names是一个字符串数组，用于指定合并同类项的变量名称
    例如:
    names = ['X','Y']
    a1 = 5X^2Y^4
    a2 = X^2YZ^3
    则返回(XY)(5XY^4 + XZ^3)

    strict:
    如果为0则不限规则
    如果为1则提取公因式的原则，每个因子必须具有相同的指数
    如果为2则只能限于两个multi_ysymbols相加

    不能合并则返回None
    返回多项式2型
    """

    ms1 = copy.deepcopy(a1)
    ms2 = copy.deepcopy(a2)

    if type(ms1) is multi_ysymbols or type(ms2) is multi_ysymbols:
        return None
    # 如果可以相加则直接相加
    if multi_ysymbols_is_can_add_or_sub(ms1, ms2) is True:
        return ypolynomial2(ms1)

    if strict < 2:
        return None

    # 找出两个multi_ysymbols相同的变量
    same_vars = []
    for name in ms1.variables:
        if len(names) != 0:
            if name not in names:
                continue
        if name in ms2.variables:
            # 公因式的指数必须相同
            if strict == 1:
                if ms1.variables[name].power != ms2.variables[name].power:
                    continue
            same_vars.append(name)

    # 没有相同的变量或者不符合合并原则则直接退出
    if len(same_vars) == 0:
        return None

    # 遍历找出的相同变量并提取最大的公因式
    remainder = ypolynomial1()

    # 取两个常数的最大公约数
    gc = gcd(ms1.const.value, ms2.const.value)

    # 消减常数项
    ms1.set_const_value(ms1.const.value() / gc)
    ms2.set_const_value(ms2.const.value / gc)
    gcd_equs = multi_ysymbols(gc)

    for name in same_vars:
        s1 = ms1.variables[name]
        s2 = ms1.variables[name]
        # 比较他们两个的次数，谁小取谁
        power = min(s1.power, s2.power)
        g = ysymbol(name=name)
        g.pow(power)
        gcd_equs.mul(g)
        # 构建余式
        r_p = s1.power - power
        if r_p == 0:
            ms1.variables.pop(name)
        else:
            ms1.variables[name].power = r_p
        r_p = s2.power - power
        if r_p == 0:
            ms2.variables.pop(name)
        else:
            ms2.variables[name].power = r_p
    p1 = ypolynomial1(ms1, ms2)
    p2 = ypolynomial2(gcd_equs, p1)
    return p2


def multi_ysymbols_exponent_extract(a):
    """
    指数提取
    X^2Y^2变为(XY)^2
    无指数提取则返回None
    返回一个多项式2型号
    """
    # 找出所有变量指数的公约数
    ms = copy.deepcopy(a)
    p_l = []
    for v in ms.variables.values():
        p_l.append(v.power)
    g = gcd(p_l)
    if ms.const.value() != 1:
        ms.const.pow(1/g)
    for v in ms.variables.values():
        v.pow(1/g)
    p2 = ypolynomial2(ms, power=g)
    return p2


def ypolynomial_merge_similar_terms(poly, names=[], strict=0):
    """
    合并同类项，因为合并的规则可以有很多这边
    1. 展开多项式
    2. 遍历列表，如果发现multi_ysymbols有相同的变量以及幂则进行合并
    """
    ret_poly = ypolynomial1()
    p = copy.deepcopy(poly).expand()
    bound = len(p)
    if bound == 0:
        return None

    used_list = []
    for i in range(bound):
        if i in used_list:
            continue

        used_list.append(i)
        ms1 = p[i]

        for j in range(bound):
            if j in used_list:
                continue

            used_list.append(j)
            ms2 = p[j]
            new_p = multi_ysymbols_merge(ms1, ms2, names, strict)

            if new_p is None:
                continue
            ret_poly.append(new_p)
    return ret_poly


def binomial_expand(poly, e=1):
    """
    二项式的扩展(x+a)^n
    根据二项式定理 $(a+b)^n = \sum_{r=0}^nC_n^ra^{n-r}b^r$
    其中C为求组合数
    poly是多项式1型号
    e是指定的指数
    """
    def __combination__(n, r):
        """
        求从n中取出r个的组合数
        $C_n^r=\frac{n!}{r!(n-r)!}$
        """
        if r > n:
            n, r = r, n
        n_f = math.factorial(n)
        r_f = math.factorial(r)
        n_r_f = math.factorial(n - r)
        return n_f / (r_f * n_r_f)

    # 确定参数多项式只有两个符号
    if len(poly) != 2:
        return None

    if type(poly) is not ypolynomial1:
        return None

    n = poly.power * e
    p = ypolynomial1()
    for r in range(0, n+1):
        power1 = n - r
        power2 = r

        ms1 = copy.deepcopy(poly[0])
        ms2 = copy.deepcopy(poly[1])

        ms1.pow(power1)
        ms2.pow(power2)
        coefficient = ysymbol(value=__combination__(n, r))

        ms = multi_ysymbols(coefficient, ms1, ms2)
        p.append(ms)
    return p


def ypolynomial_sort(poly, reverse=False, merge=False):
    """
    多项式排序
    返回多项式1型
    """
    # 这里先做扩展操作
    polynomials = copy.deepcopy(poly.expand())
    polynomials = sorted(polynomials, reverse=reverse)
    if merge is True:
        new_poly = ypolynomial_merge_similar_terms(ypolynomial1(*polynomials), strict=3)
    else:
        new_poly = ypolynomial1(*polynomials)
    return new_poly


def ypolynomial_add(p1, p2):
    """
    两个多项式相加
    1.如果两个ypolynomial1，则直接相加返回ypolynomial1型
    2.如果两个都是ypolynomial2，展开ypolynomial2，相加并返回ypolynomial1型
    3.如果两个一个是ypolynomial1，一个是ypolynomial2，则展开ypolynomial2
    相加返回ypolynomial1型

    FIX ME:这里没有考虑多项式展开后有同幂同变量的情况，所以必须保证多项式展开expand
    后的结果必须不存在同幂同变量，否则结果中有些项没有进行合并
    """
    if type(p1) is not ypolynomial1 or type(p2) is not ypolynomial1:
        raise TypeError

    v1 = copy.deepcopy(p1)
    v2 = copy.deepcopy(p2)

    p1_list = multi_ysymbols_list_x_loop_single(v1.expand())
    p2_list = multi_ysymbols_list_x_loop_single(v2.expand())

    # 调试
    # print("<debug info>list p1_list in ypolynomial_add")
    # for p in p1_list:
    #     print(p)
    # print("<debug info>list p2_list in ypolynomial_add")
    # for p in p2_list:
    #     print(p)
    p3 = None
    result = multi_ysymbols_list_add(p1_list, p2_list)
    if len(result) != 0:
        p3 = ypolynomial_sort(ypolynomial1(*result), reverse=True)
    return p3


def ypolynomial_sub(p1, p2):
    """
    两个多项式相减法，与加法类型
    """
    if type(p1) is not ypolynomial1 or type(p2) is not ypolynomial1:
        raise TypeError

    v1 = copy.deepcopy(p1)
    v2 = copy.deepcopy(p2)

    p1_list = multi_ysymbols_list_x_loop_single(v1.expand())
    p2_list = multi_ysymbols_list_x_loop_single(v2.expand())
    p3 = None
    result = multi_ysymbols_list_sub(p1_list, p2_list)
    if len(result) != 0:
        p3 = ypolynomial_sort(ypolynomial1(*result), reverse=True)
    return p3


def ypolynomial_mul(p1, p2):
    """
    两个多项式相乘法
    """
    if type(p1) is not ypolynomial1 or type(p2) is not ypolynomial1:
        raise TypeError

    items = []
    ms_list_result = []
    p1_list = multi_ysymbols_list_x_loop_single(p1.expand())
    p2_list = multi_ysymbols_list_x_loop_single(p2.expand())
    for poly1 in p1_list:
        for poly2 in p2_list:
            """
            用poly1去乘poly2_list中的每个值，并且记录到一个结果中
            """
            r = copy.deepcopy(poly1)
            r.mul(poly2)
            items.append(r)
        ms_list_result.append(copy.deepcopy(items))
        items.clear()
    # 遍历每个结果，并相加
    result = ms_list_result[0]
    for ms_list in ms_list_result[1:]:
        result = multi_ysymbols_list_add(result, ms_list)

    result = multi_ysymbols_list_x_loop_single(result)
    p3 = ypolynomial1(*result)
    return p3


def ypolynomial_div(p1, p2):
    """
    两个多项式相除法
    返回两个参数，第一个为商式，第二个为余式
    """
    if type(p1) is not ypolynomial1 or type(p2) is not ypolynomial1:
        raise TypeError
    ms1_list = multi_ysymbols_list_x_loop_single(p1.expand())
    ms2_list = multi_ysymbols_list_x_loop_single(p2.expand())

    # 找到两个多项式的最大指数，由于是逆向排序，所有拥有最大指数的ms在最前面
    ms1_max_e = ms1_list[0].max_pow()
    ms2_max_e = ms2_list[0].max_pow()

    # 如果被除式小于除数式最大指数则商式为1，余式为被除式
    if ms1_max_e < ms2_max_e:
        quotient_equ = ypolynomial1(multi_ysymbols('0'))
        remainder_equ = copy.deepcopy(p1)
        return quotient_equ, remainder_equ
    # elif ms1_max_e == ms2_max_e:
    #     # 最高幂相同，相减即可
    #     quotient_equ = ypolynomial1(multi_ysymbols('0'))
    #     remainder_equ = ypolynomial_sub(p1, p2)
    #     return quotient_equ, remainder_equ

    # 形成两个多项式的变量名列表
    def __find_same_names__():
        names_1 = set()
        names_2 = set()
        for ms in ms1_list:
            for name in ms.variables:
                names_1.add(name)
        for ms in ms2_list:
            for name in ms.variables:
                names_2.add(name)
        return names_1 | names_2, names_1 & names_2

    names, same_names = __find_same_names__()
    # 如果两个等式没有交集则直接退出
    if len(same_names) == 0:
        quotient_equ = ypolynomial1(multi_ysymbols('1'))
        remainder_equ = ypolynomial1(multi_ysymbols_sub(ms1_list, ms2_list))
        return quotient_equ, remainder_equ


    def __find_same_vars__(ms1, ms2):
        same_vars = set(list(ms1.variables)) & set(list(ms2.variables))
        return same_vars

    def __find_best_factor__(d1, d2s):
        """
        寻找最好的除数，除数与被除数差异最小
        dividend是一个multi_ysymbols类型，并且非常数
        divisors是multi_ysymbols的列表类型
        """
        def __d1_cmp_d2__(a1, a2):
            """
            忽略系数的比较
            """
            l1 = len(a1.variables)
            l2 = len(a2.variables)

            power1 = 0
            for v in a1.variables.values():
                if power1 < v.power:
                    power1 = v.power

            power2 = 0
            for v in a2.variables.values():
                if power2 < v.power:
                    power2 = v.power

            if power1 < power2:
                return -1
            elif power1 > power2:
                return 1

            # power1 == power2:
            if l1 < l2:
                return -1
            elif l1 > l2:
                return 1
            # l1 == l2:
            return 0

        if d1.is_const() is True:
            raise ValueError

        best_factor = multi_ysymbols('#', power=float('inf'))
        d1_vars = set(list(d1.variables))
        for d2 in d2s:
            if d2.is_const() is True:
                break
            # 被除数必须大于等于除数
            if __d1_cmp_d2__(d1, d2) == -1:
                continue
            # 除数之间被除数的差不为空则进行下一轮
            d2_vars = set(list(d2.variables))
            sub = d1_vars & d2_vars
            # 保证d1,d2有交集
            if sub == set():
                continue
            # 保证d2必须是d1的全子集
            if d2_vars - d1_vars != set():
                continue

            factor = multi_ysymbols('1')
            diff = d1_vars - d2_vars
            for d in diff:
                factor.mul(d1.variables[d])

            skip_it = False
            for s in sub:
                # 如果被除数的指数小于除数中的指数
                power = d1.variables[s].power - d2.variables[s].power
                if power >= 0:
                    factor.mul(multi_ysymbols(s, power=power))
                else:
                    skip_it = True
                    break
            # 如果被除数的某些变量的指数小于除数的，则跳过这个变量
            if skip_it is True:
                continue

            # 比较
            if __d1_cmp_d2__(factor, best_factor) == -1:
                best_factor = factor
                best_factor.set_const_value(yvalue_div(d1.const.get_value(),
                                                       d2.const.get_value()))
            elif __d1_cmp_d2__(factor, best_factor) == 0:
                """
                分两种情况
                1.变量相同，这时调整系数
                2.有变量不相同，这里要做更进一步的统计
                FIX ME:当前不做任何修改了
                """
                sub1 = set(list(factor))
                sub2 = set(list(best_factor))
                if sub1 == sub2:
                    pass
                else:
                    # 做更进一步的统计
                    pass
                best_factor = factor
                best_factor.set_const_value(yvalue_div(d1.const.get_value(),
                                                       d2.const.get_value()))
            else:
                pass
        return best_factor

    def __find_best_factor_list__(d1s, d2s):
        """
        找被除数项与除数项差异最大的
        """
        best_factor = multi_ysymbols('0')
        for d1 in d1s:
            if d1.is_const() is True:
                continue
            factor = __find_best_factor__(d1, d2s)
            # 如果两个式子没有因子继续
            if factor == multi_ysymbols('#', power=float('inf')):
                continue
            best_factor = factor
            #break
            # 先消去最大的幂
            # if factor > best_factor:
            #     best_factor = factor
        return best_factor

    """
     停止条件:
     1.余式的最高次数小于除式的最高次数
     2.余式的变量与除式的变量没有交集
     3.被除数为常数
     """
    quotient_equ = []
    remainder_equ = copy.deepcopy(ms1_list)
    dividend_equ = copy.deepcopy(ms1_list)
    divisor_equ = ms2_list
    while remainder_equ[0] >= divisor_equ[0]:
        factor = __find_best_factor_list__(dividend_equ, divisor_equ)
        #print("factor = %s" % factor)
        # 无任何因子则返回
        if factor == multi_ysymbols('0'):
            break
        equ = ypolynomial_mul(ypolynomial1(factor), p2)
        #print("factor * divisor = %s" % equ)
        remainder_poly = ypolynomial_sub(ypolynomial1(*dividend_equ), equ)
        #print("remainder = %s" % remainder_poly)
        remainder_equ = multi_ysymbols_list_x_loop_single(remainder_poly.expand())
        dividend_equ = remainder_equ
        quotient_equ.append(factor)
    quotient_equ = multi_ysymbols_list_x_loop_single(quotient_equ)
    # 如果商式中只有一个0则显示出来
    if len(quotient_equ) == 0:
        quotient_equ.append(multi_ysymbols('0'))
    q = ypolynomial1(*quotient_equ)
    r = ypolynomial1(*remainder_equ)
    return q, r


def ypolynomial_mod(p1, p2):
    """
    两个多项式取余
    """
    _, r = ypolynomial_div(p1, p2)
    return r


def ypolynomial_reduce(p1, n):
    """
    削减操作，用于同余运算
    """
    if type(n) is not int:
        raise TypeError
    if type(p1) is not ypolynomial1:
        raise TypeError

    result_list = []
    for p in p1.polynomials:
        v1 = p.const.value()
        #print("reduce = %d" % v1)
        if v1 % n != 0:
            result_list.append(p)
    return ypolynomial1(*result_list)


class ysymbol(object):
    """
    单符号类
    可以表示常量以及变量
    """
    def __init__(self, name="", value=0.0, prec=1000, frac_up=None, frac_down=None):
        self.is_const = True if len(name) == 0 else False
        self.power = 1
        self.__value = None
        self.set_value(value, prec, frac_up, frac_down)
        # 这里需要做变量名的判别 FIX ME
        self.name = name

    def __str__(self):
        if self.is_const is True:
            if self.value() - int(self.value()) == 0:
                return str(int(self.value()))
            return str(self.value())

        if self.power != 1:
            if self.power == float('inf'):
                return self.name + "^{\infty}"
            if self.power - int(self.power) == 0:
                return self.name + "^%d" % self.power
            return self.name + "^{%s}" % float_fraction(self.power)
        return self.name

    def __lt__(self, other):
        if type(other) is not ysymbol:
            return False
        elif self.is_const is True and other.is_const is False:
            return True
        elif self.is_const is False and other.is_const is True:
            return False
        elif self.is_const is True and other.is_const is True:
            if self.value() < other.value():
                return True
            else:
                return False
        else: #self.is_const is False and other.is_const is False:
            if self.power < other.power:
                return True
            else:
                return False

    def __gt__(self, other):
        if type(other) is not ysymbol:
            return False
        elif self.is_const is True and other.is_const is False:
            return False
        elif self.is_const is False and other.is_const is True:
            return True
        elif self.is_const is True and other.is_const is True:
            if self.value() > other.value():
                return True
            else:
                return False
        else: #self.is_const is False and other.is_const is False:
            if self.power > other.power:
                return True
            else:
                return False

    def __eq__(self, other):
        if type(other) is not ysymbol:
            return False
        elif self.is_const is True and other.is_const is False:
            return False
        elif self.is_const is False and other.is_const is True:
            return False
        elif self.is_const is True and other.is_const is True:
            if self.value() == other.value():
                return True
            else:
                return False
        else: #self.is_const is False and other.is_const is False:
            if self.power == other.power and self.name == other.name:
                return True
            else:
                return False

    def __le__(self, other):
        return not self.__gt__(other)

    def __ge__(self, other):
        return not self.__lt__(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def value(self):
        if self.__value is None:
            return 1.0 ** self.power
        # FIX ME:这是一个临时的解决方案
        if self.is_const is True:
            return self.__value.value() ** self.power
        # 如果是在求值运算中
        return gmpy2.mpz(self.__value.value()) ** self.power

    def set_value(self, value=0.0, prec=1000, frac_up=None, frac_down=None):
        if self.__value is None:
            self.__value = yvalue(value, prec, frac_up, frac_down)
        else:
            self.__value.set_value(value, prec, frac_up, frac_down)

    def get_value(self):
        return self.__value

    def be_variable(self, name="x"):
        self.name = name
        self.is_const = False
        self.power = 1
        self.__value = None

    def clear(self):
        self.name = ""
        self.is_const = True
        self.power = 1
        self.__value = None

    def pow(self, n):
        """
        指数运算
        """
        if self.is_const is True:
            v = self.value()**n
            self.__value.set_value(v)
            self.power = 1
        else:
            if n == 0:
                self.is_const = True
                self.__value.set_value(1.0)
                self.name = ""
                self.power = 1
            else:
                self.power = self.power * n

class multi_ysymbols(object):
    """
    多符号类，其中每个符号之间的关系表示相乘法
    其中是一个常数项目，多个变量项
    """
    def __init__(self, *symbols, **args):
        def __str_is_const__(s):
            """
            判断s是一个常数
            """
            if s in '1234567890.Ee/-':
                # 如果s仅是一个'.'则不是常量
                if s == '.':
                    return False
                return True
            return False

        self.const = ysymbol(value=1.0)
        self.variables = {}
        for s in symbols:
            if type(s) is ysymbol or type(s) is multi_ysymbols:
                self.mul(s)
            elif type(s) is str:
                # 分割字符串使用','字符与空格
                new_s = s.split(', ')
                for sub_s in new_s:
                    if __str_is_const__(sub_s):
                        self.mul(ysymbol(value=sub_s))
                    else:
                        self.mul(ysymbol(name=sub_s))
            else:
                raise TypeError
        if 'power' in args:
            power = args['power']
            self.pow(power)

    def __len__(self):
        if self.is_zero() is True:
            return 0
        return len(self.variables) + 1 # 1表示常量符号

    def __getitem__(self, index):
        if self.is_zero() is True:
            return None
        # 变量为零则永远返回系数部分
        if len(self.variables) == 0:
            return self.const.value()
        i = index % (len(self.variables)+1)
        if i == 0:
            return self.const.value()
        return self.variables[i-1]

    def __str__(self):
        if self.is_zero() is True:
            return "0"
        out = ""
        if self.const.value() == 1 and len(self.variables) == 0:
            out = str(self.const)
        elif self.const.value() != 1:
            out = str(self.const)
        for v in self.variables.values():
            out = out + str(v)
        return out

    def __contains__(self, item):
        if type(item) is ysymbol:
            if item.is_const is True:
                if item.value() == self.const.value():
                    return True
                return False
            if item.name in self.variables:
                return True
        elif type(item) is str:
            if item in self.variables:
                return True
        return False

    """
    变量比常量大
    变量按照指数比较
    如果所有变量的指数都一样，则按照变量个数来算
    如果都一样，则比较常量大小
    如果以上都一样，则相等
    """
    def __lt__(self, other):
        if self.is_zero() is True and other.is_zero() is True:
            return False
        elif self.is_zero() is True and other.is_zero() is False:
            return True
        elif self.is_zero() is False and other.is_zero() is True:
            return False

        if len(self.variables) == 0  and len(other.variables) != 0:
            return True
        elif len(self.variables) != 0  and len(other.variables) == 0:
            return False
        elif len(self.variables) == 0  and len(other.variables) == 0:
            if self.const.value() < other.const.value():
                return True
            return False

        # 两个都是变量，统计两边最大的指数以及变量个数
        l1 = len(self.variables)
        l2 = len(other.variables)

        power1 = 0
        for v in self.variables.values():
            if power1 < v.power:
                power1 = v.power

        power2 = 0
        for v in other.variables.values():
            if power2 < v.power:
                power2 = v.power

        if power1 < power2:
            return True
        elif power1 > power2:
            return False
        else: #power1 == power2:
            if l1 < l2:
                return True
            elif l1 == l2:
                if self.const.value() < other.const.value():
                    return True
        return False

    def __gt__(self, other):
        if self.is_zero() is True and other.is_zero() is True:
            return False
        elif self.is_zero() is True and other.is_zero() is False:
            return False
        elif self.is_zero() is False and other.is_zero() is True:
            return True

        if len(self.variables) == 0  and len(other.variables) != 0:
            return False
        elif len(self.variables) != 0  and len(other.variables) == 0:
            return True
        elif len(self.variables) == 0  and len(other.variables) == 0:
            if self.const.value() > other.const.value():
                return True
            return False

        # 两个都是变量，统计两边最大的指数以及变量个数
        l1 = len(self.variables)
        l2 = len(other.variables)

        power1 = 0
        for v in self.variables.values():
            if power1 < v.power:
                power1 = v.power

        power2 = 0
        for v in other.variables.values():
            if power2 < v.power:
                power2 = v.power

        if power1 > power2:
            return True
        elif power1 < power2:
            return False
        else: #power1 == power2:
            if l1 > l2:
                return True
            elif l1 == l2:
                if self.const.value() > other.const.value():
                    return True
        return False

    def __eq__(self, other):
        if self.is_zero() is True and other.is_zero() is True:
            return True
        if len(self.variables) == 0  and len(other.variables) == 0:
            if self.const.value() == other.const.value():
                return True
            return False

        # 两个都是变量，统计两边最大的指数以及变量个数
        l1 = len(self.variables)
        l2 = len(other.variables)

        power1 = 0
        for v in self.variables.values():
            if power1 < v.power:
                power1 = v.power

        power2 = 0
        for v in other.variables.values():
            if power2 < v.power:
                power2 = v.power

        if power1 == power2 and l1 == l2:
            if self.const.value() == other.const.value():
                return True
        else:
            return False
        return False

    def __le__(self, other):
        return not self.__gt__(other)

    def __ge__(self, other):
        return not self.__lt__(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __exponent__(self, n):
        self.const.pow(n)
        for v in self.variables.values():
            v.pow(n)

    def is_const(self):
        return len(self.variables) == 0

    def set_const_value(self, sval=None, prec=1000, fru=None, frd=None):
        """
        设置常量值，如果常量值为0，则整体为0
        """
        self.const.set_value(sval, prec, fru, frd)
        if self.const.value() == 0:
            self.set_zero()

    def set_variable_value(self, name, val):
        if type(name) is not str:
            raise TypeError

        if name in self.variables:
            self.variables[name].set_value(val)

    def is_zero(self):
        if self.const.value() == 0:
            if len(self.variables) != 0:
                self.set_zero()
            return True
        return False

    def set_zero(self):
        self.variables.clear()
        self.const = yvalue(0.0)

    def is_one(self):
        if self.is_const():
            if self.const.value() == 1:
                return True
        return False

    def max_pow(self):
        """
        当前multi_ysymbols的最大指数
        """
        max_e = -1
        for ms in self.variables.values():
            max_e = max(max_e, ms.power)
        return max_e

    def pow(self, n):
        """
        指数运算，顺便设置了指数扩展
        """
        if self.is_zero() is True:
            return
        if n == 0:
            self.set_const_value(1.0)
            self.variables.clear()
            return
        self.__exponent__(n)

    def mul(self, *symbols):
        """
        symbols可以是一个列表，一次进行多个数的相乘
        """
        if len(symbols) != 0:
            for s in symbols:
                # 如果是常数则合并常数
                if type(s) is ysymbol:
                    if s.is_const is True:
                        # 当常数为0时，那么这个多符号结构直接设置0属性并返回
                        if s.value() == 0:
                            self.set_zero()
                            return
                        v = yvalue_mul(self.const.value(), s.value())
                        self.set_const_value(v)
                    else:
                        # 如果在已经存在符号则合并指数
                        if s.name in self.variables:
                            self.variables[s.name].power += s.power
                            # 这里可能某个power为负数，则如果为0删除这个变量
                            if self.variables[s.name].power == 0:
                                self.variables.pop(s.name)
                        else:
                            self.variables[s.name] = copy.deepcopy(s)
                elif type(s) is multi_ysymbols:
                    if s.is_zero() is True:
                        self.set_zero()
                        return
                    else:
                        """
                        因为以下是递归调用，所以这里不用再次调用set_zero()
                        这里都会抛出异常，则这里不处理
                        """
                        self.mul(s.const)
                        for v in s.variables.values():
                            self.mul(v)
                else:
                    continue
        return

    def eval(self):
        result = gmpy2.mpz(1.0)
        for v in self.variables.values():
            result *= gmpy2.mpz(v.value())
        result *= gmpy2.mpz(self.const.value())
        return result


class ypolynomial(object):
    """
    多项式的父类型号，因为会派生两个多项式类型
    1类表示一个或多个polynomial与multi_ysymbols类型的加法
    2类表示一个或多个polynomial与multi_ysymbols类型的乘法
    """
    def __init__(self, *syms, **args):
        self.polynomials = []
        if 'power' in args:
            self.power = args['power']
        else:
            self.power = 1
        self.append(*syms)

    def __len__(self):
        return len(self.polynomials)

    def __getitem__(self, index):
        if len(self.polynomials) == 0:
            return None
        i = index % len(self.polynomials)
        return self.polynomials[i]

    def append(self, *syms):
        if len(syms) != 0:
            for s in syms:
                if type(s) is ysymbol:
                    ms = multi_ysymbols(s)
                    self.polynomials.append(ms)
                elif type(s) is multi_ysymbols:
                    self.polynomials.append(s)
                elif type(s) is ypolynomial1 or type(s) is ypolynomial2:
                    self.polynomials.append(s)
                elif type(s) is str:
                    self.polynomials.append(multi_ysymbols(s))
                else:
                    continue
        return len(self.polynomials)

    def set_variables_value(self, **args):
        for a in args:
            for p in self.polynomials:
                p.set_variable_value(a, args[a])


class ypolynomial1(ypolynomial):
    """
    多项式结构1型号，其中的每个元素是multi_ysymbols或者polynomial，每个元素的关系表示'+'
    """
    def __init__(self, *syms, **args):
        ypolynomial.__init__(self, *syms, **args)

    def __str__(self):
        if len(self.polynomials) == 0:
            return ""
        out = ""
        i = 0
        ms_list = self.expand()
        for ms in ms_list:
            if i != 0:
                if ms.is_zero() is True:
                    i += 1
                    continue
                if ms.const.value() > 0:
                    out += ('+' + str(ms))
                else:
                    out += str(ms)
            else:
                out = str(ms)
            i += 1
        return out

    def expand(self):
        """
        将表达式展开，如果遇到多项式1型号和2型号，则进行展开
        """
        res = []
        for s in self.polynomials:
            if type(s) is multi_ysymbols:
                res.append(s)
            else: #type(s) == polynomial(1|2):
                res.extend(s.expand())
        return res

    def eval(self):
        result = gmpy2.mpz(0.0)
        for p in self.polynomials:
            result += p.eval()
        result = result ** self.power
        return result


class ypolynomial2(ypolynomial):
    """
    多项式结构2型号，其中的每个元素是multi_ysymbols或者polynomial，每个元素的关系表示'*'
    """
    def __init__(self, *syms, **args):
        ypolynomial.__init__(self, *syms, **args)

    def __str__(self):
        if len(self.polynomials) == 0:
            return ""
        out = ""
        for p in self.polynomials:
            if type(p) is ypolynomial1:
                out = out + '(' + str(p) + ')'
            else:
                out = out + str(p)
        if self.power != 1:
            out = '(' + out + ')^%d' % self.power
        return out

    def __merge__(self, ms1, ms2):
        """
        ms1, ms2是两个列表
        """
        if type(ms1) is not list or type(ms2) is not list:
            return None
        res = []
        for s1 in ms1:
            s = s1
            l = []
            for s2 in ms2:
                s.mul(s2)
                l.append(s)
            res.extend(l)
        return res

    def expand(self):
        """
        将表达式展开，如果遇到多项式1型号和2型号，则进行展开
        """
        res = []
        for s in self.polynomials:
            if type(s) is multi_ysymbols:
                res.append(s)
            else: #type(s) == polynomial(1|2):
                p = s.expand()
                # 与当前所有展开的表达式合并
                if len(res) != 0:
                    res = self.__merge__(res, p)
                else:
                    res.extend(p)
        return res

    def eval(self):
        result = gmpy2.mpz(1.0)
        for p in self.polynomials:
            result *= p.eval()
        result = result ** self.power
        return result


if __name__ == "__main__":
    #pdb.set_trace()
    x = ysymbol(name='x')
    a = ysymbol(name="a")
    a.pow(2)
    c1 = ysymbol(value=5)
    c2 = ysymbol(value=8)
    y = ysymbol(name='y')
    y.pow(2)
    b = ysymbol(name="b")
    m1 = multi_ysymbols(c1,x,b)
    m2 = multi_ysymbols(c2,y,a)
    #P1 = ypolynomial1(m1, m2)
    #print("P1 = %s" % P1)
    P2 = ypolynomial1(x, ysymbol(name="a"))
    P2 = binomial_expand(P2, 7)
    print("P2 = %s" % P2)
    x.pow(5)
    P3 = ypolynomial1(x, ysymbol(value=-1.0))
    print("P3 = %s" % P3)
    P4_q, P4_r = ypolynomial_div(P2, P3)
    print("P4_q = %s" % P4_q)
    print("P4_r = %s" % P4_r)
    #P5 = ypolynomial_add(ypolynomial_mul(P4_q, P3), P4_r)
    #print("P5 = %s" % P5)
    #rd = ypolynomial_reduce(P4_r, 31)
    #print(rd)
    #rd.set_variables_value(x=4, a=5)
    #print(rd.eval())

    #P2 = ypolynomial_sort(P2, reverse=True)
    #print("P2 = %s" % P2)


    # P2 = ypolynomial_add(P2, ypolynomial1(multi_ysymbols(c1, x, b)))
    # print(P2)
    # P3 = ypolynomial_sub(P1, P2)
    # print(P3)
    # P4 = ypolynomial_mul(P1, P2)
    # print(P4)
else:
    pass
