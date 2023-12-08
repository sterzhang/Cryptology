import os
import random

class AES:

    MIX_C  = [[0x2, 0x3, 0x1, 0x1], [0x1, 0x2, 0x3, 0x1], [0x1, 0x1, 0x2, 0x3], [0x3, 0x1, 0x1, 0x2]]
    I_MIXC = [[0xe, 0xb, 0xd, 0x9], [0x9, 0xe, 0xb, 0xd], [0xd, 0x9, 0xe, 0xb], [0xb, 0xd, 0x9, 0xe]]
    RCon   = [0x01000000, 0x02000000, 0x04000000, 0x08000000, 0x10000000, 0x20000000, 0x40000000, 0x80000000, 0x1B000000, 0x36000000]

    S_BOX = [[0x63, 0x7C, 0x77, 0x7B, 0xF2, 0x6B, 0x6F, 0xC5, 0x30, 0x01, 0x67, 0x2B, 0xFE, 0xD7, 0xAB, 0x76],
             [0xCA, 0x82, 0xC9, 0x7D, 0xFA, 0x59, 0x47, 0xF0, 0xAD, 0xD4, 0xA2, 0xAF, 0x9C, 0xA4, 0x72, 0xC0],
             [0xB7, 0xFD, 0x93, 0x26, 0x36, 0x3F, 0xF7, 0xCC, 0x34, 0xA5, 0xE5, 0xF1, 0x71, 0xD8, 0x31, 0x15],
             [0x04, 0xC7, 0x23, 0xC3, 0x18, 0x96, 0x05, 0x9A, 0x07, 0x12, 0x80, 0xE2, 0xEB, 0x27, 0xB2, 0x75],
             [0x09, 0x83, 0x2C, 0x1A, 0x1B, 0x6E, 0x5A, 0xA0, 0x52, 0x3B, 0xD6, 0xB3, 0x29, 0xE3, 0x2F, 0x84],
             [0x53, 0xD1, 0x00, 0xED, 0x20, 0xFC, 0xB1, 0x5B, 0x6A, 0xCB, 0xBE, 0x39, 0x4A, 0x4C, 0x58, 0xCF],
             [0xD0, 0xEF, 0xAA, 0xFB, 0x43, 0x4D, 0x33, 0x85, 0x45, 0xF9, 0x02, 0x7F, 0x50, 0x3C, 0x9F, 0xA8],
             [0x51, 0xA3, 0x40, 0x8F, 0x92, 0x9D, 0x38, 0xF5, 0xBC, 0xB6, 0xDA, 0x21, 0x10, 0xFF, 0xF3, 0xD2],
             [0xCD, 0x0C, 0x13, 0xEC, 0x5F, 0x97, 0x44, 0x17, 0xC4, 0xA7, 0x7E, 0x3D, 0x64, 0x5D, 0x19, 0x73],
             [0x60, 0x81, 0x4F, 0xDC, 0x22, 0x2A, 0x90, 0x88, 0x46, 0xEE, 0xB8, 0x14, 0xDE, 0x5E, 0x0B, 0xDB],
             [0xE0, 0x32, 0x3A, 0x0A, 0x49, 0x06, 0x24, 0x5C, 0xC2, 0xD3, 0xAC, 0x62, 0x91, 0x95, 0xE4, 0x79],
             [0xE7, 0xC8, 0x37, 0x6D, 0x8D, 0xD5, 0x4E, 0xA9, 0x6C, 0x56, 0xF4, 0xEA, 0x65, 0x7A, 0xAE, 0x08],
             [0xBA, 0x78, 0x25, 0x2E, 0x1C, 0xA6, 0xB4, 0xC6, 0xE8, 0xDD, 0x74, 0x1F, 0x4B, 0xBD, 0x8B, 0x8A],
             [0x70, 0x3E, 0xB5, 0x66, 0x48, 0x03, 0xF6, 0x0E, 0x61, 0x35, 0x57, 0xB9, 0x86, 0xC1, 0x1D, 0x9E],
             [0xE1, 0xF8, 0x98, 0x11, 0x69, 0xD9, 0x8E, 0x94, 0x9B, 0x1E, 0x87, 0xE9, 0xCE, 0x55, 0x28, 0xDF],
             [0x8C, 0xA1, 0x89, 0x0D, 0xBF, 0xE6, 0x42, 0x68, 0x41, 0x99, 0x2D, 0x0F, 0xB0, 0x54, 0xBB, 0x16]]

    I_SBOX = [[0x52, 0x09, 0x6A, 0xD5, 0x30, 0x36, 0xA5, 0x38, 0xBF, 0x40, 0xA3, 0x9E, 0x81, 0xF3, 0xD7, 0xFB],
              [0x7C, 0xE3, 0x39, 0x82, 0x9B, 0x2F, 0xFF, 0x87, 0x34, 0x8E, 0x43, 0x44, 0xC4, 0xDE, 0xE9, 0xCB],
              [0x54, 0x7B, 0x94, 0x32, 0xA6, 0xC2, 0x23, 0x3D, 0xEE, 0x4C, 0x95, 0x0B, 0x42, 0xFA, 0xC3, 0x4E],
              [0x08, 0x2E, 0xA1, 0x66, 0x28, 0xD9, 0x24, 0xB2, 0x76, 0x5B, 0xA2, 0x49, 0x6D, 0x8B, 0xD1, 0x25],
              [0x72, 0xF8, 0xF6, 0x64, 0x86, 0x68, 0x98, 0x16, 0xD4, 0xA4, 0x5C, 0xCC, 0x5D, 0x65, 0xB6, 0x92],
              [0x6C, 0x70, 0x48, 0x50, 0xFD, 0xED, 0xB9, 0xDA, 0x5E, 0x15, 0x46, 0x57, 0xA7, 0x8D, 0x9D, 0x84],
              [0x90, 0xD8, 0xAB, 0x00, 0x8C, 0xBC, 0xD3, 0x0A, 0xF7, 0xE4, 0x58, 0x05, 0xB8, 0xB3, 0x45, 0x06],
              [0xD0, 0x2C, 0x1E, 0x8F, 0xCA, 0x3F, 0x0F, 0x02, 0xC1, 0xAF, 0xBD, 0x03, 0x01, 0x13, 0x8A, 0x6B],
              [0x3A, 0x91, 0x11, 0x41, 0x4F, 0x67, 0xDC, 0xEA, 0x97, 0xF2, 0xCF, 0xCE, 0xF0, 0xB4, 0xE6, 0x73],
              [0x96, 0xAC, 0x74, 0x22, 0xE7, 0xAD, 0x35, 0x85, 0xE2, 0xF9, 0x37, 0xE8, 0x1C, 0x75, 0xDF, 0x6E],
              [0x47, 0xF1, 0x1A, 0x71, 0x1D, 0x29, 0xC5, 0x89, 0x6F, 0xB7, 0x62, 0x0E, 0xAA, 0x18, 0xBE, 0x1B],
              [0xFC, 0x56, 0x3E, 0x4B, 0xC6, 0xD2, 0x79, 0x20, 0x9A, 0xDB, 0xC0, 0xFE, 0x78, 0xCD, 0x5A, 0xF4],
              [0x1F, 0xDD, 0xA8, 0x33, 0x88, 0x07, 0xC7, 0x31, 0xB1, 0x12, 0x10, 0x59, 0x27, 0x80, 0xEC, 0x5F],
              [0x60, 0x51, 0x7F, 0xA9, 0x19, 0xB5, 0x4A, 0x0D, 0x2D, 0xE5, 0x7A, 0x9F, 0x93, 0xC9, 0x9C, 0xEF],
              [0xA0, 0xE0, 0x3B, 0x4D, 0xAE, 0x2A, 0xF5, 0xB0, 0xC8, 0xEB, 0xBB, 0x3C, 0x83, 0x53, 0x99, 0x61],
              [0x17, 0x2B, 0x04, 0x7E, 0xBA, 0x77, 0xD6, 0x26, 0xE1, 0x69, 0x14, 0x63, 0x55, 0x21, 0x0C, 0x7D]]
    
    # 设置固定的种子
    random.seed(12345)
    # 生成一个16字节的伪随机IV
    IV = bytes([random.randint(0, 255) for _ in range(16)])
    Nounce = bytes([random.randint(0, 255) for _ in range(8)])

    def SubBytes(self, State):
        # 字节替换
        return [self.S_BOX[i][j] for i, j in 
               [(_ >> 4, _ & 0xF) for _ in State]]

    def SubBytes_Inv(self, State):
        # 字节逆替换
        return [self.I_SBOX[i][j] for i, j in
               [(_ >> 4, _ & 0xF) for _ in State]]

    def ShiftRows(self, S):
        # 行移位
        return [S[ 0], S[ 5], S[10], S[15], 
                S[ 4], S[ 9], S[14], S[ 3],
                S[ 8], S[13], S[ 2], S[ 7],
                S[12], S[ 1], S[ 6], S[11]]

    def ShiftRows_Inv(self, S):
        # 逆行移位
        return [S[ 0], S[13], S[10], S[ 7],
                S[ 4], S[ 1], S[14], S[11],
                S[ 8], S[ 5], S[ 2], S[15],
                S[12], S[ 9], S[ 6], S[ 3]]

    def MixColumns(self, State):
        # 列混合
        return self.Matrix_Mul(self.MIX_C, State)

    def MixColumns_Inv(self, State):
        # 逆列混合
        return self.Matrix_Mul(self.I_MIXC, State)

    def RotWord(self, _4byte_block):
        # 用于生成轮密钥的字移位
        return ((_4byte_block & 0xffffff) << 8) + (_4byte_block >> 24)

    def SubWord(self, _4byte_block):
        # 用于生成密钥的字节替换
        result = 0
        for position in range(4):
            i = _4byte_block >> position * 8 + 4 & 0xf
            j = _4byte_block >> position * 8 & 0xf
            result ^= self.S_BOX[i][j] << position * 8
        return result

    def mod(self, poly, mod = 0b100011011):  
        # poly模多项式mod
        while poly.bit_length() > 8:
            poly ^= mod << poly.bit_length() - 9
        return poly

    def mul(self, poly1, poly2):
        # 多项式相乘
        result = 0
        for index in range(poly2.bit_length()):
            if poly2 & 1 << index:
                result ^= poly1 << index
        return result

    def Matrix_Mul(self, M1, M2):  # M1 = MIX_C  M2 = State
        # 用于列混合的矩阵相乘
        M = [0] * 16
        for row in range(4):
            for col in range(4):
                for Round in range(4):
                    M[row + col*4] ^= self.mul(M1[row][Round], M2[Round+col*4])
                M[row + col*4] = self.mod(M[row + col*4])
        return M

    def round_key_generator(self, _16bytes_key):
        # 轮密钥产生
        w = [_16bytes_key >> 96, 
             _16bytes_key >> 64 & 0xFFFFFFFF, 
             _16bytes_key >> 32 & 0xFFFFFFFF, 
             _16bytes_key & 0xFFFFFFFF] + [0]*40
        for i in range(4, 44):
            temp = w[i-1]
            if not i % 4:
                temp = self.SubWord(self.RotWord(temp)) ^ self.RCon[i//4-1]
            w[i] = w[i-4] ^ temp
        return [self.num_2_16bytes(
                    sum([w[4 * i] << 96, w[4*i+1] << 64, 
                         w[4*i+2] << 32, w[4*i+3]])
                    ) for i in range(11)]

    def AddRoundKey(self, State, RoundKeys, index):
        # 异或轮密钥
        return self._16bytes_xor(State, RoundKeys[index])

    def _16bytes_xor(self, _16bytes_1, _16bytes_2):
        return [_16bytes_1[i] ^ _16bytes_2[i] for i in range(16)]

    def _16bytes2num(cls, _16bytes):
        # 16字节转数字
        return int.from_bytes(_16bytes, byteorder = 'big')
    def _32bytes2num(cls, _32bytes):
        # 32字节转数字
        return int.from_bytes(_32bytes, byteorder = 'big')
    
    def num_2_16bytes(cls, num):
        # 数字转16字节
        return num.to_bytes(16, byteorder = 'big')
    def num_2_32bytes(cls, num):
        # 数字转32字节
        return num.to_bytes(32, byteorder = 'big')
    
    # AES + ECB(电码本模式)
    def aes_encrypt(self, plaintext, RoundKeys):

        # 将明文分割成128位（16字节）的块
        plaintext_blocks = [plaintext[i:i+16] for i in range(0, len(plaintext), 16)]

        encrypted_blocks = []
        for plaintext_block in plaintext_blocks:
            State = plaintext_block
            State = self.AddRoundKey(State, RoundKeys, 0)
            for Round in range(1, 10):
                State = self.SubBytes(State)
                State = self.ShiftRows(State)
                State = self.MixColumns(State)
                State = self.AddRoundKey(State, RoundKeys, Round)
            State = self.SubBytes(State)
            State = self.ShiftRows(State)
            State = self.AddRoundKey(State, RoundKeys, 10)
            State = bytes(State)  # 将列表转换为字节序列
            encrypted_blocks.append(State)
        
        # 将加密后的块合并为一个字节序列
        encrypted_data = b''.join(encrypted_blocks)
        return encrypted_data


    def aes_decrypt(self, ciphertext, RoundKeys):
        # 将密文分割成128位（16字节）的块
        ciphertext_blocks = [ciphertext[i:i+16] for i in range(0, len(ciphertext), 16)]

        decrypted_blocks = []
        for ciphertext_block in ciphertext_blocks:
            State = ciphertext_block
            State = self.AddRoundKey(State, RoundKeys, 10)
            for Round in range(1, 10):
                State = self.ShiftRows_Inv(State)
                State = self.SubBytes_Inv(State)
                State = self.AddRoundKey(State, RoundKeys, 10 - Round)
                State = self.MixColumns_Inv(State)
            State = self.ShiftRows_Inv(State)
            State = self.SubBytes_Inv(State)
            State = self.AddRoundKey(State, RoundKeys, 0)
            State = bytes(State)  # 将列表转换为字节序列
            decrypted_blocks.append(State)

        # 将解密后的块合并为一个字节序列
        decrypted_data = b''.join(decrypted_blocks)
        return decrypted_data
        

    # AES + CBC(密文分组模式)
    def xor_blocks(self, block1, block2):
        return bytes([b1 ^ b2 for b1, b2 in zip(block1, block2)])

    def aes_encrypt_cbc(self, plaintext, RoundKeys):
        # 初始化向量
        iv = self.IV  # 确保在类中定义了IV

        # 将明文分割成128位（16字节）的块
        plaintext_blocks = [plaintext[i:i+16] for i in range(0, len(plaintext), 16)]

        # 检查最后一个块的长度并进行特殊填充
        if len(plaintext_blocks[-1]) < 16:
            last_block = plaintext_blocks[-1]
            padding_needed = 16 - len(last_block)
            last_block += b'\x80' + b'\x00' * (padding_needed - 1)
            plaintext_blocks[-1] = last_block

        encrypted_blocks = []
        previous_block = iv
        for plaintext_block in plaintext_blocks:
            # 将当前明文块与前一个加密块（或IV）异或
            State = self.xor_blocks(plaintext_block, previous_block)

            # 加密异或后的块
            State = self.AddRoundKey(State, RoundKeys, 0)
            for Round in range(1, 10):
                State = self.SubBytes(State)
                State = self.ShiftRows(State)
                State = self.MixColumns(State)
                State = self.AddRoundKey(State, RoundKeys, Round)
            State = self.SubBytes(State)
            State = self.ShiftRows(State)
            State = self.AddRoundKey(State, RoundKeys, 10)

            # 保存加密块，用作下一个块的IV
            previous_block = State
            State = bytes(State)  # 将列表转换为字节序列
            encrypted_blocks.append(State)
        
        # 将加密后的块合并为一个字节序列
        encrypted_data = b''.join(encrypted_blocks)
        return encrypted_data

    def aes_decrypt_cbc(self, ciphertext, RoundKeys):
        
        iv = self.IV

        # 将密文分割成128位（16字节）的块
        ciphertext_blocks = [ciphertext[i:i+16] for i in range(0, len(ciphertext), 16)]

        decrypted_blocks = []
        previous_block = iv
        for ciphertext_block in ciphertext_blocks:
            # 解密块
            State = ciphertext_block
            State = self.AddRoundKey(State, RoundKeys, 10)
            for Round in range(9, 0, -1):
                State = self.ShiftRows_Inv(State)
                State = self.SubBytes_Inv(State)
                State = self.AddRoundKey(State, RoundKeys, Round)
                State = self.MixColumns_Inv(State)
            State = self.ShiftRows_Inv(State)
            State = self.SubBytes_Inv(State)
            State = self.AddRoundKey(State, RoundKeys, 0)

            # 将解密后的块与前一个密文块（或IV）异或
            State = self.xor_blocks(State, previous_block)
            decrypted_blocks.append(State)

            # 更新previous_block为当前的密文块
            previous_block = ciphertext_block
        
        # 将解密后的块合并为一个字节序列
        decrypted_data = b''.join(decrypted_blocks)

        return decrypted_data


    # AES + OFB(输出反馈模式)
    def aes_encrypt_ofb(self, plaintext, RoundKeys):

        # 将明文分割成128位（16字节）的块
        plaintext_blocks = [plaintext[i:i+16] for i in range(0, len(plaintext), 16)]

        encrypted_blocks = []
        output_block = self.IV

        for plaintext_block in plaintext_blocks:
            State = output_block
            State = self.AddRoundKey(State, RoundKeys, 0)
            for Round in range(1, 10):
                State = self.SubBytes(State)
                State = self.ShiftRows(State)
                State = self.MixColumns(State)
                State = self.AddRoundKey(State, RoundKeys, Round)
            State = self.SubBytes(State)
            State = self.ShiftRows(State)
            State = self.AddRoundKey(State, RoundKeys, 10)
            State = bytes(State)  # 将列表转换为字节序列
            output_block = State
            encrypted_block = self.xor_blocks(State, plaintext_block)
            encrypted_blocks.append(encrypted_block)
        
        # 将加密后的块合并为一个字节序列
        encrypted_data = b''.join(encrypted_blocks)
        return encrypted_data
    
    def aes_decrypt_ofb(self, ciphertext, RoundKeys):

        # 将明文分割成128位（16字节）的块
        ciphertext_blocks = [ciphertext[i:i+16] for i in range(0, len(ciphertext), 16)]

        decrypted_blocks = []
        output_block = self.IV

        for ciphertext_block in ciphertext_blocks:
            State = output_block
            State = self.AddRoundKey(State, RoundKeys, 0)
            for Round in range(1, 10):
                State = self.SubBytes(State)
                State = self.ShiftRows(State)
                State = self.MixColumns(State)
                State = self.AddRoundKey(State, RoundKeys, Round)
            State = self.SubBytes(State)
            State = self.ShiftRows(State)
            State = self.AddRoundKey(State, RoundKeys, 10)
            State = bytes(State)  # 将列表转换为字节序列
            output_block = State
            decrypted_block = self.xor_blocks(State, ciphertext_block)
            decrypted_blocks.append(decrypted_block)
        
        # 将加密后的块合并为一个字节序列
        decrypted_data = b''.join(decrypted_blocks)
        return decrypted_data

    # AES + CFB(密文反馈模式)
    def aes_encrypt_cfb(self, plaintext, RoundKeys):

        # 将明文分割成128位（16字节）的块
        plaintext_blocks = [plaintext[i:i+16] for i in range(0, len(plaintext), 16)]

        encrypted_blocks = []
        output_block = self.IV

        for plaintext_block in plaintext_blocks:
            State = output_block
            State = self.AddRoundKey(State, RoundKeys, 0)
            for Round in range(1, 10):
                State = self.SubBytes(State)
                State = self.ShiftRows(State)
                State = self.MixColumns(State)
                State = self.AddRoundKey(State, RoundKeys, Round)
            State = self.SubBytes(State)
            State = self.ShiftRows(State)
            State = self.AddRoundKey(State, RoundKeys, 10)
            State = bytes(State)  # 将列表转换为字节序列
            encrypted_block = self.xor_blocks(State, plaintext_block)
            encrypted_blocks.append(encrypted_block)
            output_block = encrypted_block
        
        # 将加密后的块合并为一个字节序列
        encrypted_data = b''.join(encrypted_blocks)
        return encrypted_data

    def aes_decrypt_cfb(self, ciphertext, RoundKeys):

        # 将明文分割成128位（16字节）的块
        ciphertext_blocks = [ciphertext[i:i+16] for i in range(0, len(ciphertext), 16)]

        decrypted_blocks = []
        output_block = self.IV

        for ciphertext_block in ciphertext_blocks:
            State = output_block
            State = self.AddRoundKey(State, RoundKeys, 0)
            for Round in range(1, 10):
                State = self.SubBytes(State)
                State = self.ShiftRows(State)
                State = self.MixColumns(State)
                State = self.AddRoundKey(State, RoundKeys, Round)
            State = self.SubBytes(State)
            State = self.ShiftRows(State)
            State = self.AddRoundKey(State, RoundKeys, 10)
            State = bytes(State)  # 将列表转换为字节序列
            decrypted_block = self.xor_blocks(State, ciphertext_block)
            decrypted_blocks.append(decrypted_block)
            output_block = ciphertext_block
        
        # 将加密后的块合并为一个字节序列
        decrypted_data = b''.join(decrypted_blocks)
        return decrypted_data


    # AES + CTR(计数器模式)
    def aes_encrypt_ctr(self, plaintext, RoundKeys):
        # 将明文分割成128位（16字节）的块
        plaintext_blocks = [plaintext[i:i+16] for i in range(0, len(plaintext), 16)]

        encrypted_blocks = []
        counter = 0

        for plaintext_block in plaintext_blocks:
            # 构造计数器块
            counter_block = self.Nounce + counter.to_bytes(16 - len(self.Nounce), byteorder='big')

            # 加密计数器块而不是明文块
            State = counter_block
            State = self.AddRoundKey(State, RoundKeys, 0)
            for Round in range(1, 10):
                State = self.SubBytes(State)
                State = self.ShiftRows(State)
                State = self.MixColumns(State)
                State = self.AddRoundKey(State, RoundKeys, Round)
            State = self.SubBytes(State)
            State = self.ShiftRows(State)
            State = self.AddRoundKey(State, RoundKeys, 10)
            State = bytes(State)  # 将列表转换为字节序列

            # 将加密后的计数器块与明文块进行异或操作
            encrypted_block = self.xor_blocks(State, plaintext_block)
            encrypted_blocks.append(encrypted_block)

            # 增加计数器
            counter += 1

        # 将加密后的块合并为一个字节序列
        encrypted_data = b''.join(encrypted_blocks)
        return encrypted_data

    def aes_decrypt_ctr(self, ciphertext, RoundKeys):
        # 将密文分割成128位（16字节）的块
        ciphertext_blocks = [ciphertext[i:i+16] for i in range(0, len(ciphertext), 16)]

        decrypted_blocks = []
        counter = 0

        for ciphertext_block in ciphertext_blocks:
            # 构造计数器块
            counter_block = self.Nounce + counter.to_bytes(16 - len(self.Nounce), byteorder='big')

            # 加密计数器块
            State = counter_block
            State = self.AddRoundKey(State, RoundKeys, 0)
            for Round in range(1, 10):
                State = self.SubBytes(State)
                State = self.ShiftRows(State)
                State = self.MixColumns(State)
                State = self.AddRoundKey(State, RoundKeys, Round)
            State = self.SubBytes(State)
            State = self.ShiftRows(State)
            State = self.AddRoundKey(State, RoundKeys, 10)
            State = bytes(State)  # 将列表转换为字节序列

            # 将加密后的计数器块与密文块进行异或操作
            decrypted_block = self.xor_blocks(State, ciphertext_block)
            decrypted_blocks.append(decrypted_block)

            # 增加计数器
            counter += 1

        # 将解密后的块合并为一个字节序列
        decrypted_data = b''.join(decrypted_blocks)
        return decrypted_data




if __name__ == '__main__':

    aes = AES()
    #128bit的密钥
    key = 0x000102030405060708090a0b0c0d0e0f 
    RoundKeys = aes.round_key_generator(key)

    # 加密
    plaintext = 0x00112233445566778899aabbccddeeff00112233445566778899aabbccddeeff
    # print(type(plaintext))
    plaintext = aes.num_2_32bytes(plaintext)
    # print(type(plaintext))
    ciphertext = aes.aes_encrypt_ctr(plaintext, RoundKeys)
    print('ciphertext = ' + hex(aes._32bytes2num(ciphertext)))

    # 解密
    # ciphertext = 0x69c4e0d86a7b0430d8cdb78070b4c55a
    ciphertext = 0xd74a56da41a0113c4b45a4b9ea9c3c865c55e41214b06ca04e8a43d61617b9b9
    ciphertext = aes.num_2_32bytes(ciphertext)
    plaintext = aes.aes_decrypt_ctr(ciphertext, RoundKeys)
    print('plaintext = ' + hex(aes._32bytes2num(plaintext)))
