from main import DES
from utils import str2binaryArray, binaryArray2Str
from workingMode import ENCODE, DECODE
import re

with open('./utils.py', 'r', encoding='utf-8') as f:
    data = ''.join(f.readlines())
    # 将文本文件转换为二进制字符串数组, 类似['01100011', '01101111', ...]
    binaryStrArray = str2binaryArray(data, encoding='utf-8')
    # 前面需要补充多少个0
    zerosPre = '00000000' * (8 - len(binaryStrArray) % 8)

    # 前面填好0后，形成明文, 一整个字符串，长度为64的倍数
    M = zerosPre + ''.join(binaryStrArray)
    # 密匙
    key = '0001001100110100010101110111100110011011101111001101111111110001'

    # 将明文进行加密密文
    groups = re.compile(r'[01]{64}').findall(M)  # 分割为64位一组
    C = ''  # 密文
    for subStr in map(lambda str: DES(key, str, ENCODE), groups):
        C += ''.join(subStr)

    # 解密后的明文
    groups = re.compile(r'[01]{64}').findall(C)  # 分割为64位一组
    M1 = ''
    for subStr in map(lambda str: DES(key, str, DECODE), groups):
        M1 += ''.join(subStr)

    # 将解密后的明文还原为原来的文本
    text = binaryArray2Str(M1)
    print(text)
