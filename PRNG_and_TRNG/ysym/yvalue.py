#!/usr/bin/python
# coding:utf-8
import copy
from ysym.ymath import *
import gmpy2  # https://github.com/aleaxit/gmpy/
"""
为符号库，提供基本的数值保存类，分数功能比较强
"""


def yvalue_valid_type(v):
    if type(v) is yvalue or type(v) is int or type(v) is float:
        return True
    if is_mpfr(v) or is_mpz(v):
        return True
    elif type(v) is str:
        for s in str:
            if s not in '1234567890Ee-./':
                return False
        return True
    return False


def yvalue_calc_frac(frac):
    """
    将frac进行展开并计算最终得float值
    如果frac类型非yyvalue则返回None
    """
    fru = gmpy2.mpfr(0.0)
    frd = gmpy2.mpfr(0.0)

    if type(frac) is float or type(frac) is int:
        # 忽略数值违法得错误 FIX ME
        if frac == 0:
            return gmpy2.mpfr(0.0)
        return gmpy2.mpfr(frac)

    if type(frac) is yvalue:
        if type(frac.frac_up) is yvalue:
            fru = yvalue_calc_frac(frac.frac_up)
        else:
            fru = frac.frac_up
        if type(frac.frac_down) is yvalue:
            frd = yvalue_calc_frac(frac.frac_down)
        else:
            frd = frac.frac_down
        # 忽略数值违法得错误 FIX ME
        if fru == 0 or frd == 0:
            return gmpy2.mpfr(0.0)
    return gmpy2.mpfr(fru / frd)


def yvalue_args_check_and_return(y1, y2):
    v1 = None
    v2 = None
    if type(y1) is not yvalue and type(y2) is not yvalue:
        if yvalue_valid_type(y1) and yvalue_valid_type(y2):
            v1 = yvalue(y1)
            v2 = yvalue(y2)
        else:
            return None, None
    elif type(y1) is not yvalue and type(y2) is yvalue:
        if yvalue_valid_type(y1):
            v1 = yvalue(y1)
            v2 = copy.deepcopy(y2)
        else:
            return None, None
    elif type(y1) is yvalue and type(y2) is not yvalue:
        if yvalue_valid_type(y2):
            v1 = copy.deepcopy(y1)
            v2 = yvalue(y2)
        else:
            return None, None
    else:
        v1 = copy.deepcopy(y1)
        v2 = copy.deepcopy(y2)
    return v1, v2


def yvalue_uniformity(y1, y2):
    """
    同分
    返回三个值
    y1的分子，y2的分子,分母
    无法同分则返回None,None,None
    """
    v1, v2 = yvalue_args_check_and_return(y1, y2)
    if v1 is None:
        return None

    v1.merge_frac()
    v2.merge_frac()

    # merge_frac过后，可以保证v1,v2只有一层
    v1_u = v1.frac_up
    v1_d = v1.frac_down
    v2_u = v2.frac_up
    v2_d = v2.frac_down

    d = v1_d * v2_d
    v1_u = v1_u * v2_d
    v2_u = v2_u * v1_d

    return v1_u, v2_u, d


def yvalue_add(y1, y2):
    """
    只要发生错误，则返回0数值
    """
    v1, v2 = yvalue_args_check_and_return(y1, y2)
    if v1 is None:
        return None

    v1u, v2u, v12d = yvalue_uniformity(v1, v2)
    if v1u is None:
        return None
    return yvalue(fru=v1u+v2u, frd=v12d)


def yvalue_sub(y1, y2):
    v1, v2 = yvalue_args_check_and_return(y1, y2)
    if v1 is None:
        return None

    v1u, v2u, v12d = yvalue_uniformity(v1, v2)
    if v1u is None:
        return None
    return yvalue(fru=v1u-v2u, frd=v12d)


def yvalue_mul(y1, y2):
    v1, v2 = yvalue_args_check_and_return(y1, y2)
    if v1 is None:
        return None

    v1.merge_frac()
    v2.merge_frac()

    v1_u = v1.frac_up
    v1_d = v1.frac_down
    v2_u = v2.frac_up
    v2_d = v2.frac_down
    r = yvalue(fru=v1_u * v2_u, frd=v1_d * v2_d)
    r.reduction_of_fraction()
    return r


def yvalue_div(y1, y2):
    v1, v2 = yvalue_args_check_and_return(y1, y2)
    if v1 is None:
        return None

    v1.merge_frac()
    v2.merge_frac()

    v1_u = v1.frac_up
    v1_d = v1.frac_down
    v2_u = v2.frac_up
    v2_d = v2.frac_down
    r = yvalue(fru=v1_u * v2_d, frd=v2_u * v1_d)
    r.reduction_of_fraction()
    return r


def yvalue_to_common(s, d):
    """
    返回一个yvalue使得
    r * s = d
    无法达到则返回None
    """
    vs, vd = yvalue_args_check_and_return(s, d)
    if vs is None:
        return None

    if s.value() == 0 and d.value() != 0:
        return None

    if d.value() == 0:
        return yvalue('0')

    if d == s:
        return yvalue('1')
    return yvalue(fru=d, frd=s)


class yvalue(object):
    """
    数值类型
    支持科学计数以及分数录入，不符合语法则将数值设定为1.0
    """
    def __init__(self, sval=None, prec=1000, fru=None, frd=None):
        r = self.set_value(sval, prec, fru, frd)
        if r == 0:
            self.__value = gmpy2.mpfr(0.0)
            self.frac_up = gmpy2.mpfr(0.0)
            self.frac_down = gmpy2.mpfr(1.0)

    def __str__(self):
        if self.frac_up == 0:
            return "0"
        return ("\\frac{%s}{%s}" % (str(self.frac_up), str(self.frac_down)))

    def __repr__(self):
        return self.__str__()

    def __lt__(self, other):
        if type(other) is float or type(other) is int:
            return self.value() < other
        elif type(other) is yvalue:
            return self.value() < other.value()
        return False

    def __gt__(self, other):
        if type(other) is float or type(other) is int:
            return self.value() > other
        elif type(other) is yvalue:
            return self.value() > other.value()
        return False

    def __eq__(self, other):
        if type(other) is float or type(other) is int:
            return self.value() == other
        elif type(other) is yvalue:
            return self.value() == other.value()
        return False

    def __le__(self, other):
        return not self.__gt__(other)

    def __ge__(self, other):
        return not self.__lt__(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __is_float__(self, flt):
        if flt == 0:
            return False
        if gmpy2.mpfr(flt) - gmpy2.mpz(flt) == 0:
            return False
        return True

    def __is_integer__(self, flt):
        return not self.__is_float__(flt)

    def __float_fraction_str__(self, flt=0.5, prec=1000):
        """
        浮点数换分数
        返回分数字符串
        """
        f_up, f_down = float_fraction(flt, prec)
        return ("\\frac{%s}{%s}" % (str(f_up), str(f_down)))

    def __be_zero__(self):
        self.__value = gmpy2.mpfr(0.0)
        self.frac_up = gmpy2.mpfr(0.0)
        self.frac_down = gmpy2.mpfr(1.0)

    def __merge_frac__(self, frac):
        """
        merge_frac的递归支持函数
        frac 是分数
        连续递归处理分子与分母，递归完毕后，进行合并最终合并成一个分子一个分母
        """
        # 如果分子是一个分数
        if type(frac.frac_up) is yvalue:
            u_, d_ = frac.frac_up.merge_frac()
            # 分母是一个分数
            if type(frac.frac_down) is yvalue:
                _u, _d = frac.frac_down.merge_frac()
                u = u_ * _d
                d = d_ * _u
                # 约分
                g = gcd(u, d)
                if g != 1:
                    frac_up = u / g
                    frac_down = d / g
                else:
                    frac_up = u
                    frac_down = d
            else:
                # 如果分母是一个整数
                frac_down = frac.frac_down
                u = u_
                d = d_ * frac_down
                # 约分
                g = gcd(u, d)
                if g != 1:
                    frac_up = u / g
                    frac_down = d / g
                else:
                    frac_up = u
                    frac_down = d
        else:
            # 如果分子是整数
            frac_up = frac.frac_up
            if type(frac.frac_down) is yvalue:
                _u, _d = frac.frac_down.merge_frac()
                u = frac_up * _d
                d = _u
                # 约分
                g = gcd(u, d)
                if g != 1:
                    frac_up = u / g
                    frac_down = d / g
                else:
                    frac_up = u
                    frac_down = d
            else:
                # 如果分母是整数
                frac_down = frac.frac_down
        return frac_up, frac_down

    def merge_frac(self):
        """
        将分子或者分母为分数得形式一一进行合并
        执行此函数之后，保证yvalue的frac_up与frac_down都是整数
        """
        frac_up_u = gmpy2.mpfr(0.0)
        frac_up_d = gmpy2.mpfr(0.0)
        frac_down_u = gmpy2.mpfr(0.0)
        frac_down_d = gmpy2.mpfr(0.0)
        if type(self.frac_up) is yvalue:
            frac_up_u, frac_up_d = self.__merge_frac__(self.frac_up)
        else:
            frac_up_u = self.frac_up
            frac_up_d = gmpy2.mpfr(1.0)

        if type(self.frac_down) is yvalue:
            frac_down_u, frac_down_d = self.__merge_frac__(self.frac_down)
        else:
            frac_down_u = self.frac_down
            frac_down_d = gmpy2.mpfr(1.0)

        # 交叉相乘
        self.frac_up = frac_up_u * frac_down_d
        self.frac_down = frac_up_d * frac_down_u
        u, d = self.reduction_of_fraction()
        return u, d

    def reduction_of_fraction(self):
        """
        约分
        仅处理分子分母都是整数
        """
        if type(self.frac_up) is yvalue or type(self.frac_down) is yvalue:
            return None, None

        g = gcd(self.frac_up, self.frac_down)
        self.frac_up = self.frac_up / g
        self.frac_down = self.frac_down / g
        return self.frac_up, self.frac_down

    def value(self):
        v = yvalue_calc_frac(self)
        self.__value = v
        return v

    def set_value(self, sval=None, prec=1000, fru=None, frd=None):
        """
        设置值
        """
        self.__value = gmpy2.mpfr(1.0)
        self.frac_up = gmpy2.mpfr(1.0)
        self.frac_down = gmpy2.mpfr(1.0)

        def __str_in_it__(str, str_set):
            for s in str:
                if s not in str_set:
                    return False
            return True

        # 检查字符串，只能限定数字以及Ee以及负号与除号，小数点
        if sval is not None:
            if type(sval) is str:
                if __str_in_it__(sval, '1234567890Ee-./') is False:
                    return self.__value
                if sval[0].isdigit() is False:
                    return self.__value
                # 如果是分数形式,但是这里只能进行一层的分割，语法没有进行处理
                # FIX ME
                if '/' in sval:
                    s = sval.split('/')
                    if len(s) != 2:
                        return self.__value
                    # 这里可能是浮点或者分数，但是这里也没有做语法的判断
                    # FIX ME
                    #if s[0].isdigit() is False or s[1].isdigit() is False:
                    #    return self.__value
                    frac_up = float(s[0])
                    if frac_up == 0:
                        self.__be_zero__()
                        return self.__value
                    if self.__is_float__(frac_up) is True:
                        self.frac_up = yvalue(frac_up)
                    else:
                        self.frac_up = frac_up
                    frac_down = float(s[1])
                    if frac_down == 0:
                        self.__be_zero__()
                        return self.__value
                    if self.__is_float__(frac_down) is True:
                        self.frac_down = yvalue(frac_down)
                    else:
                        self.frac_down = frac_down
                    self.__value = frac_up / frac_down
                else: # python会自动转换科学计数法
                    frac_up, frac_down = float_fraction(gmpy2.mpfr(sval), prec)
                    self.frac_up = frac_up
                    self.frac_down = frac_down
                    if frac_up == 0 or frac_down == 0:
                        self.__value = gmpy2.mpfr(0.0)
                        if frac_down == 0:
                            self.__be_zero__()
                    else:
                        self.__value = frac_up / frac_down
            elif type(sval) is yvalue:
                self.__value = sval.__value
                self.frac_up = sval.frac_up
                self.frac_down = sval.frac_down
            else: # 整型或者浮点数
                frac_up, frac_down = float_fraction(gmpy2.mpfr(sval), prec)
                self.frac_up = frac_up
                self.frac_down = frac_down
                if frac_up == 0 or frac_down == 0:
                    self.__value = gmpy2.mpfr(0.0)
                    if frac_down == 0:
                        self.__be_zero__()
                else:
                    self.__value = frac_up / frac_down
        else: # sval is None
            if fru is not None and frd is None:
                self.__value = yvalue_calc_frac(fru)
                self.frac_up = fru.frac_up
                self.frac_down = fru.frac_down
            elif fru is None and frd is not None:
                self.frac_down = gmpy2.mpfr(1.0)
                self.frac_up = gmpy2.mpfr(1.0)
                return self.__value
            elif fru is None and frd is None:
                return self.__value
            else:
                self.frac_up = fru
                self.frac_down = frd
                if self.frac_down == 0:
                    return None
                frac_up = yvalue_calc_frac(fru)
                frac_down = yvalue_calc_frac(frd)
                self.__value = frac_up / frac_down
        return self.__value


if __name__ == "__main__":
    #pdb.set_trace()
    v1 = yvalue('5342354982849321759402749032174314932107947320947312097594274932174123.5/6')
    v2 = yvalue('3')
    if v1 == v2:
        print('yes')
    else:
        print('no')
    v3 = yvalue_add(v1, v2)
    print('v1 + v2 = %s,%f' % (v3, v3.value()))
    v4 = yvalue_mul(v1, v2)
    print('v1 * v2 = %s,%f' % (v4, v4.value()))
    v5 = yvalue_div(v1, v2)
    print('v1 / v2 = %s,%f' % (v5, v5.value()))
    v6 = yvalue_sub(v1, v2)
    print('v1 - v2 = %s,%f' % (v6, v6.value()))
    v7 = yvalue(fru=v3, frd=v4)
    print("v7 = %s,%f" % (v7, v7.value()))
    print(v7.merge_frac())
    #v3 = yvalue("3.14e-3", 1000000)
    #print(v3)
    #print(v3.value)
else:
    pass
