import random

# 定义一个函数生成给定数的所有质因数
def generate_prime_factors(n):
    i = 2
    prime_factors = []
    while i * i <= n:
        if n % i:
            i += 1
        else:
            n //= i
            if i not in prime_factors:
                prime_factors.append(i)
    if n > 1:
        prime_factors.append(n)
    return prime_factors

# 定义一个函数找到给定素数p的本原根
def find_primitive_root(p):
    # 在一个给定的素数p的情况下，寻找一个本原根g。对于任何小于p的正整数a，都可以找到一个整数k，使得g^k mod p = a。即g的幂在模p意义下可以生成从1到p-1的所有数字。

    # 由于p是素数，所以order的质因数只有2和(p-1)/2
    order = p - 1   # phi(p)欧拉函数

    if p == 2:
        return 1
    
    prime_factors = generate_prime_factors(order)

    # 随机选择一个数g，从2到p-1之间
    while True:
        g = random.randint(2, order)

        flag = False
        for factor in prime_factors:
            # 对于每个g，它检查g的所有order的质因数的幂是否模p等于1，如果结果是1，那么g不是本原根，需要选择另一个g重试；如果g对所有质因数的检验都不等于1，那么g就是一个本原根
            if pow(g, order // factor, p) == 1:
                flag = True
                break
        if flag:
            continue
        return g


def generate_keys(prime):
    '''generates public_key, private_key pair'''

    # 1.选择大质数p，并选择p的本原元g
    p = prime
    g = find_primitive_root(p)
    # 2.选择随机数x，注意这里的x不能超过p
    x = random.randint(1, (p - 1) // 2)
    # 3.得到g1
    g1 = pow(g, x, p)

    private_key = x
    public_key = g1
    # 将（g1，x）作为密钥，g1是公钥，这里随机选取的x是私钥，g是本原元
    return (public_key, private_key), g


def encrypt(public_key, prime, g):
    '''返回encrypted_msg和ephemeral_key'''

    print("on other side...")
    secret_message = int(input('Enter any message to encrypt: '))
    # 1.随机选取随机数r，原算法中取值应该是2≤y≤p-2，这里为了简化
    r = random.randint(1, (prime - 1) // 2)
    # 2.计算与密文计算相关的C1（ephemeral_key）和C2（(secret_message * masking_key) % prime）
    ephemeral_key = pow(g, r, prime)
    masking_key = pow(public_key, r, prime)

    # 返回C2，C1
    return (secret_message * masking_key) % prime, ephemeral_key


# the owner side生成公私钥
prime_number = int(input('Enter any prime number（eg.1237): '))
print('Generating keys...')
keys, generator = generate_keys(prime_number)
public_key, private_key = keys
print(f'public key: {public_key}, private_key: {private_key}')
print('sending public_key, prime_number, generator publicly.....\n')

# 将公私钥下发给encrypt side，利用公钥g和g1加密，并

# C1为短钥ephemeral_key，C2为cipher
cipher, ephemeral_key = encrypt(public_key, prime_number, generator)
# what we recieve is a cipher and temporary session key called "ephermeral_key"
print('Encrypting...')
print('ciphertext:', cipher, 'ephemeral_key:', ephemeral_key)
print()

# decrypt the encrypted message on our side
# computing the masking key from ephermeral_key
print('Decrypting...')
print('Computing Masking key (use ephemeral_key)...')
# pow用于计算C1^-a，根据费马小定理，对任何整数a和素数p，如果a不是p的倍数，那么a^p-1 mod p = 1，所以这里a^p-1-d实际上是a^d的模逆
masking_key = pow(ephemeral_key, prime_number - 1 - keys[1])

# decipher
decipher = (cipher * masking_key) % prime_number
print('decrypted:', decipher)