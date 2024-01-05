from Crypto.Cipher import DES
from Crypto.Util.Padding import pad, unpad
import itertools
import time

def des_encrypt(plaintext, key):
    cipher = DES.new(key, DES.MODE_ECB)
    padded_text = pad(plaintext, DES.block_size)
    return cipher.encrypt(padded_text)

def des_decrypt(ciphertext, key):
    cipher = DES.new(key, DES.MODE_ECB)
    decrypted_data = cipher.decrypt(ciphertext)
    try:
        return unpad(decrypted_data, DES.block_size)
    except ValueError:
        return decrypted_data

def brute_force_des(ciphertext, expected_plaintext):
    # 对于非常短的4位密钥，我们可以尝试所有可能的密钥组合
    for key_part in itertools.product(range(256), repeat=5):
        # 生成8字节的密钥，前4字节为密钥部分，后4字节填充为0
        # print(key_part)
        key_bytes = bytes(key_part) + b'\x00\x00\x00'
        try:
            decrypted_text = des_decrypt(ciphertext, key_bytes)
            if decrypted_text == expected_plaintext:
                return key_bytes
        except ValueError:
            continue
    return None

# 加密和暴力破解
plaintext = b'ABCDEFGH'  # DES要求8字节的数据块
key = b'\x00\x00\x10\x12\x00' + b'\x00\x00\x00'  # 示例密钥
ciphertext = des_encrypt(plaintext, key)


print("------origin-------")

print(f"plaintext:{plaintext}")
print(f"key:{key}")
print(f"ciphertext:{ciphertext}")

print("----after break-----")

# 开始计时
start_time = time.time()
# 破解过程
found_key = brute_force_des(ciphertext, plaintext)
if found_key:
    print("暴力破解成功:", found_key)
else:
    print("暴力破解失败")

print(f"plaintext:{plaintext}")
print(f"found key:{found_key}")
print(f"ciphertext used by found key:{des_encrypt(plaintext, found_key)}")

# 结束计时
end_time = time.time()

# 计算并打印执行时间
execution_time = end_time - start_time
print("执行时间:", execution_time, "秒")