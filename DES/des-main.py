#Jianshu Zhang
#DES
import binascii
import base64

import des_components as init

def format_binary(value, bits, space_interval=8):
    bin_str = format(value, '0' + str(bits) + 'b') 
    spaced_str = ' '.join(bin_str[i:i+space_interval] for i in range(0, len(bin_str), space_interval))
    return spaced_str

#permutation process
def Permu(block, block_len, table):
    #init return result
    bit_result = 0
    #look up table
    for x in table:
        #get the x's number, and use it to shift the block
        cur_bit = (block>>(block_len - x)) & 0x1
        #shifting the bit_result left for 1 bit, and adding the cur_bit to the base bit of bit_result
        bit_result = (bit_result<<1) | cur_bit
    return bit_result

#generate keys for every 16 rounds
def gen_keys(C0, D0):
    #save each round's key in a dict
    keys= dict.fromkeys(range(0,17))
    #import left rotate values 
    shifts = init.left_rotate_values

    #define a function of shift left(the overflow parts will go to the base of the value)
    f_sl = lambda val, shift_left_number, max_bit: \
        (val << shift_left_number % max_bit) & (2**max_bit - 1) | \
        ((val & (2**max_bit - 1))) >> (max_bit - (shift_left_number % max_bit))

    #initialize C0, D0
    C0 = f_sl(C0, 0, 28)
    D0 = f_sl(D0, 0, 28)
    keys[0] = (C0, D0)

    #generate keys for each round
    for i, sf in enumerate(shifts, start=1):
        C_old = keys[i-1][0]
        D_old = keys[i-1][1]
        Ci = f_sl(C_old, sf, 28)
        Di = f_sl(D_old, sf, 28)
        keys[i] = (Ci, Di)

    #merge 28,28 -> 56
    f_merge = lambda c, d, bits: \
      (c & (2**bits - 1)) << bits | (d & (2**bits - 1))
    
    #save 1st ~ 16th keys
    del keys[0]
    for key in keys.keys():
        c = keys[key][0]
        d = keys[key][1]
        K_i = f_merge(c, d, 28)
        K_i = Permu(K_i, 56, init.PC2)
        keys[key] = K_i

    return keys




def S_box(R_i):
    #save 8 partitions, each parts have 6 bits
    parts = []
    for i in range(7, -1, -1):
        #0x3f -> 11 1111
        x = (R_i >> (i*6) & (0x3f))
        parts.append(x)
    
    #transfer the orgin 6 digits to 4 digits corresponds to Sbox
    for i in range(8):
        part = parts[i]
        #head and rear combine to the row
        row = (((part >> 5) & 0x1) << 1) | (part & 0x1)
        #4 middle digits combine to the col
        col = (part >> 1) & 0xf
        parts[i] = init.Sboxes[i][row*16+col]

    R_i = 0
    for i in range(8):
        part = parts[i]
        R_i = (R_i << 4) | (part & 0xf)
    
    return R_i

def count_bit_diffs(a, b):
    """Count the number of different bits"""
    return bin(a ^ b).count('1')

def test_s_box_properties(S_box_func, s_boxes):
    test_passed = True

    # ①:输出不是输入的线性和仿射函数
    for x in range(64):
        for y in range(64):
            if S_box_func(x ^ y) == S_box_func(x) ^ S_box_func(y):
                print(f"非线性未通过")
                test_passed = False
                break

    for c in range(1, 64):  # 常数c从1到63
        constant = None
        for x in range(64):
            result = S_box_func(x) ^ S_box_func(x ^ c)
            if constant is None:
                constant = result  # 第一次设定比较标准
            elif result != constant:
                break  
        else:
            # 如果完成了所有x的遍历且没有中断，则S盒可能是仿射的
            print(f"S盒可能是仿射的，c={c:06b}")
            test_passed = False

    # ②:任意改变输入中的一位，输出至少有两位发生变化
    for i in range(64):  # 对于所有64种可能的6位输入
        original_input = i
        original_output = S_box_func(original_input)

        for j in range(6):  # 改变输入的每一位
            modified_input = original_input ^ (1 << j)
            modified_output = S_box_func(modified_input)

            if count_bit_diffs(original_output, modified_output) < 2:
                print(f"②未通过: 输入 {original_input:06b} 和 {modified_input:06b}")
                test_passed = False

    # ③:对于任何S盒和任何输入x，S(x)和S(x⊕001100)至少有两位不同，这里x是一个6位的二进制串
    for i in range(64): 
        original_input = i
        original_output = S_box_func(original_input)
        modified_input = original_input ^ 0b001100  # XOR with 001100
        modified_output = S_box_func(modified_input)

        if count_bit_diffs(original_output, modified_output) < 2:
            print(f"③未通过: 输入 {original_input:06b} 和 {modified_input:06b}")
            test_passed = False
    
    # ④:对于任何S盒和任何输入x，以及y,z∈GF(2)，S(x)≠S(x⊕11yz00)，这里x是一个6位的二进制串
    for x in range(64):  
        for y in range(2):  # y为0或1
            for z in range(2):  # z为0或1
                x_prime = x ^ (0b110000 | (y << 3 | z << 2))
                if S_box_func(x) == S_box_func(x_prime):
                    print(f"④未通过: 输入 {x:06b} 和 {x_prime:06b}")
                    test_passed = False

    # ⑤:保持输入中的1位不变，其余5位变化，输出中的0和1的个数接近相等
    for fixed_bit in range(6):  # 对于每个固定位
        count_0 = 0
        count_1 = 0
        for x in range(64):  
            if (x >> fixed_bit) & 1 == 0:  # 如果固定位是0
                if S_box_func(x) & 1 == 0:  # 如果输出的最低位是0
                    count_0 += 1
                else:
                    count_1 += 1
        if abs(count_0 - count_1) > 2:  # 根据某个阈值2判断是否平衡
            print(f"⑤未通过: 固定位 {fixed_bit}")
            test_passed = False

    return test_passed


# F round function   
def Func(R_i, K_i):
    #Step1. R_i(32bits) --E--> R_i(48bits)
    #permutate R_i using E table
    R_i = Permu(R_i, 32, init.E)
    
    #Step2. R_i | K_i+1
    #R_i | K_i+1
    R_i = R_i ^ K_i
    print("R_i ^ K_i:{}".format(format_binary(R_i, 48)))
    #Step3. 48bits -> 32bits using S box
    R_i = S_box(R_i)
    print("S_box(R_i):{}".format(format_binary(R_i, 32)))
    #Step4. Pertubation using P
    R_i = Permu(R_i, 32, init.P)

    return R_i


def DES(message, key, decrypt=False):
    if decrypt:
        print("Decrypting")
    else:
        print("Crypting")

    key_binary_str = "{:064b}".format(key)
    key_binary_str_grouped = ' '.join([key_binary_str[i:i+8] for i in range(0, len(key_binary_str), 8)])
    print("Original Key: ", key_binary_str_grouped)

    
    print("\n\n*****DES step1. 64bits key --PC1--> 56bits key*****")
    #DES step1. 64bits key --PC1--> 56bits key
    key = Permu(key, 64, init.PC1)

    key_binary_str = "{:056b}".format(key)
    key_binary_str_grouped = ' '.join([key_binary_str[i:i+8] for i in range(0, len(key_binary_str), 8)])
    print("Key after PC1 permutation: ", key_binary_str_grouped)

    #generate 16 keys for each iteration
    C0 = (key >> 28) & 0xfffffff
    D0 = (key) & 0xfffffff

    keys = gen_keys(C0, D0)
    print("--------16 keys----------")
    for key, value in keys.items():
        print("Key {}: {}".format(key, format_binary(value, 48)))  
    print("-------------------------")

    
    print("\n\n*****DES step2. permutate 64bits message using IP******")
    #DES step2. permutate 64bits message using IP

    message_binary_str = "{:064b}".format(message)
    message_binary_str_grouped = ' '.join([message_binary_str[i:i+8] for i in range(0, len(message_binary_str), 8)])
    print("Original Message: ", message_binary_str_grouped)
    
    message = Permu(message, 64, init.IP)

    message_binary_str = "{:064b}".format(message)
    message_binary_str_grouped = ' '.join([message_binary_str[i:i+8] for i in range(0, len(message_binary_str), 8)])
    print("Message after IP: ", message_binary_str_grouped)


    print("\n\n*****DES step3. split the 64bits message to 32bits L0 and R0******")
    #DES step3. split the 64bits message to 32bits L0 and R0
    L0 = (message >> 32) & 0xffffffff
    R0 = message & 0xffffffff
    

    print("\n\n*****DES step4. apply round function 16 times******")    
    #DES step4. apply round function 16 times
    L_last = L0
    R_last = R0

    print("L0:{}".format(format_binary(L_last, 32)))
    print("R0:{}\n".format(format_binary(R_last, 32)))

    if decrypt:
        for i in range(16,0,-1):
            tmp = L_last
            L_last = R_last
            R_last = Func(R_last, keys[i]) ^ tmp
    else:
        for i in range(1,17):
            tmp = L_last
            L_last = R_last
            R_last = Func(R_last, keys[i]) ^ tmp
            print("K{}:{}".format(i,format_binary(keys[i], 48)))
            # if i%8 == 0:
            print("L{}:{}".format(i,format_binary(L_last, 32)))
            print("R{}:{}\n".format(i,format_binary(R_last, 32)))
            


    #DES step5. combine the last round of R,L together to get the final result
    result_message = ((R_last & 0xffffffff) << 32) | (L_last & 0xffffffff)

    ##DES step6. permutate result using IP_INV
    result_message = Permu(result_message, 64, init.IP_INV)

    return result_message

def decrypt(message, key):
    decrypted_message = DES(message, key, decrypt=True)
    #return as format of hex(except for '0x')
    return bytearray.fromhex(str(hex(decrypted_message))[2:]).decode

def binary_str_to_int(binary_str):
    return int(binary_str.replace(" ", ""), 2)

def int_to_binary_str(number, length):
    return format(number, '0' + str(length) + 'b')


# test data
key_binary = "00110001 00110010 00110011 00110100 00110101 00110110 00110111 00111000"
input_data_binary = "00110000 00110001 00110010 00110011 00110100 00110101 00110110 00110111"
expected_output_binary = "10001011 10110100 01111010 00001100 11110000 10101001 01100010 01101101"

# bin str -> int
key = binary_str_to_int(key_binary)
input_data = binary_str_to_int(input_data_binary)
expected_output = binary_str_to_int(expected_output_binary)

# encrypt
encrypted_data = DES(input_data, key,decrypt=False)

# int -> bin str
encrypted_data_binary = int_to_binary_str(encrypted_data, 64)

# test
if encrypted_data_binary == expected_output_binary.replace(" ", ""):
    print("successful encrypting!")
else:
    print("error when testing")
    print("encrypted_data_binary：", encrypted_data_binary)

print("---------------------------------------------------------------------\n\n")
# decrypt
decrypted_data = DES(encrypted_data, key,decrypt=True)

# int -> bin str
decrypted_data_binary = int_to_binary_str(decrypted_data, 64)

# test
if decrypted_data_binary == input_data_binary.replace(" ", ""):
    print("successful decrypting!")
else:
    print("error when testing")
    print("decrypted_data_binary：", decrypted_data_binary)



# test of S box
if test_s_box_properties(S_box, init.Sboxes):
    print("Successful")
else:
    print("Error")
