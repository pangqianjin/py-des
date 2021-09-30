import os.path
import re
import shelve
import time

from tables.sBox import sBox
from workingMode import ENCODE, DECODE
from tables.ipReplacementTable import ipReplacementTable
from tables.keyReplacementTable import keyReplacementTable
from tables.shiftLeftTable import shiftLeftTable
from tables.compressTable import compressTable
from tables.expansionTable import expansionTable
from tables.pBox import pBox
from tables.finalTable import finalTable

Ki = []


def initKi(key: str, mode: str = ENCODE) -> None:
    """
    初始化Ki数组
    :param key:初始提供的密钥
    :param mode:加密模式还是解密模式
    :return:
    """
    # 置换后的56位key，不包含8个奇偶校验位
    replacedKey = list(map(lambda index: key[index - 1], keyReplacementTable))
    Ci = replacedKey[:28]
    Di = replacedKey[28:]

    for i in range(16):
        # Ci和Di循环左移j次
        for j in range(shiftLeftTable[i]):
            head = Ci[0]
            Ci = Ci[1:]
            Ci.append(head)

            head = Di[0]
            Di = Di[1:]
            Di.append(head)
        # Ci和Di压缩成48位
        CiDi = []
        CiDi.extend(Ci)
        CiDi.extend(Di)
        K = list(map(lambda index: CiDi[index - 1], compressTable))
        Ki.append(K)
    if mode == DECODE:
        Ki.reverse()


def F(R: list, K: list) -> list:
    """
    F函数
    :param R:长度为32的字符数组
    :param K:长度为48的字符数组
    :return:R从32位拓展置换到48位，K压缩置换后还是48位，二者再异或运算，然后S盒置换，P盒置换
    """
    # E盒拓展置换
    expandedR = list(map(lambda index: R[index - 1], expansionTable))
    # 异或运算
    XORed = binaryArrayXOR(K, expandedR)
    # S盒置换
    sBoxToTransform = sliceXORed(XORed)
    sBoxTransformed = []
    index = 0
    for subArr in sBoxToTransform:
        sBoxTransformed.extend(strTransformBySBox(subArr, 's{}'.format(index + 1)))
        index += 1
    # P盒置换
    pBoxTransformed = list(map(lambda index: sBoxTransformed[index - 1], pBox))
    return pBoxTransformed


def DES(key: str, data: str, mode: str = ENCODE) -> list:
    """
    DES算法
    :param key:DES算法的工作密匙，64位
    :param data:要被加密或被解密的数据，64位
    :param mode:DES的工作模式
    :return:加密或解密后的64位数据
    """
    # IP置换
    replacedData = list(map(lambda index: data[index - 1], ipReplacementTable))
    L0 = replacedData[:32]
    R0 = replacedData[32:]
    # Ki的初始化
    initKi(key, mode)
    # Li盒和Ri的初始化
    Li = L0
    Ri = R0
    # 16轮迭代
    for i in range(16):
        K = Ki[i]
        f = F(Ri, K)

        tmp = Li
        Li = Ri
        Ri = binaryArrayXOR(tmp, f)
    # 最终置换
    RiLi = []
    RiLi.extend(Ri)
    RiLi.extend(Li)
    finalTransformed = list(map(lambda index: RiLi[index - 1], finalTable))
    # 验证加密
    # print(''.join(finalTransformed)=='1000010111101000000100110101010000001111000010101011010000000101')
    # 验证解密
    # print(''.join(finalTransformed)=='0000000100100011010001010110011110001001101010111100110111101111')
    return finalTransformed


# DES('0001001100110100010101110111100110011011101111001101111111110001',
#     '0000000100100011010001010110011110001001101010111100110111101111', ENCODE)
# # DES('0001001100110100010101110111100110011011101111001101111111110001',
# #     '1000010111101000000100110101010000001111000010101011010000000101', DECODE)

def binaryArrayXOR(arr1: list, arr2: list) -> list:
    """
    将两个二进制字符数组进行异或运算，如['0', '1', '0']^['0', '0', '1']=['0', '1', '1']
    :param arr1: 二进制字符数组1
    :param arr2: 二进制字符数组2
    :return: list
    """
    res = []
    for i in range(len(arr1)):
        res.append(str(int(arr1[i]) ^ int(arr2[i])))
    return res


def sliceXORed(arr: list) -> list:
    """
    将长度为48的数组转换为带有8个长度为6的子数组的新数组
    :param arr: 长度为48的字符数组或字符串
    :return:返回带有8个子数组的新数组，其中每个子数组长度为6
    """
    res = [[], [], [], [], [], [], [], []]
    for i in range(48):
        index = int(i / 6)
        res[index].append(arr[i])
    return res


def strTransformBySBox(arr: list, sBoxIndex: str) -> list:
    """
    s盒转换，根据sBoxIndex的值确定是哪个s盒, 将一个长度为6的字符数组进行s盒转换，并返回长度为4的字符数组
    :param arr:待转换的字符数组，长度为6
    :param sBoxIndex:可选值: 's1', 's2', 's3', 's4', 's5', 's6', 's7', 's8'
    :return:返回一个s盒中对应的十进制数的二进制形式的字符数组，长度为4
    """
    row = int(arr[0] + arr[5], 2)
    col = int(''.join(arr[1:5]), 2)
    binaryStr = bin(sBox[sBoxIndex][row][col])[2:]

    res = ['0' for i in range(4 - len(binaryStr))]
    res.extend(list(binaryStr))

    return res


def str2binaryArray(string: bytes) -> list:
    """
    将任意bytes串 转换为一个二进制字符数组，长度大于等于8且无上限
    :param string:被解析的bytes串
    :return:返回值为一个字符串数组，其中每一个字符串都是长度为8的0/1字符串
    """
    binaryStrs = [bin(b)[2:] for b in string]

    return list(map(lambda b: '0' * (8 - len(b)) + b, binaryStrs))


def binaryArray2Str(string: str, left: int) -> bytes:
    """
    将一个0/1字符串转换为bytes
    :param string:0/1字符串
    :param left: 需要去掉左侧填充的字符数
    :return:
    """
    groups = re.compile(r'[01]{8}').findall(string)[int(left / 8):]  # 8位一组

    return bytes([int(str, 2) for str in groups])


def encodeFile(pathname: str, key: str = '0001001100110100010101110111100110011011101111001101111111110001') -> (
        str, int):
    """
    将一个文件转为01字符串的密文，并返回这个密文和前面填充了多少个0
    :param pathname: 要加密的文件的路径名
    :param key: 密匙
    :return: 01字符串密文和左侧填充0的个数
    """
    with open(pathname, 'rb') as f:
        startTime = time.time()
        print('正在加密{}...'.format(pathname), end='')

        data = f.read()
        # 将文本文件转换为二进制字符串数组, 类似['01100011', '01101111', ...]
        binaryStrArray = str2binaryArray(data)
        # 前面需要补充多少个0
        zerosPre = '00000000' * (8 - len(binaryStrArray) % 8)

        # 前面填好0后，形成明文, 一整个字符串，长度为64的倍数
        M = zerosPre + ''.join(binaryStrArray)

        # 将明文进行加密密文
        groups = re.compile(r'[01]{64}').findall(M)  # 分割为64位一组
        C = ''  # 密文
        for subStr in map(lambda str: DES(key, str, ENCODE), groups):
            C += ''.join(subStr)

        endTime = time.time()
        print('耗时{}s!'.format(endTime - startTime))

        return C, len(zerosPre)


def decodeText(string: str, left: int,
               key: str = '0001001100110100010101110111100110011011101111001101111111110001') -> bytes:
    """
    将01密文字符串还原为原来的bytes
    :param string: 01密文字符串
    :param left: 左侧填充的0的个数
    :param key: 密匙
    :return: 原来的bytes
    """
    # 解密后的明文
    groups = re.compile(r'[01]{64}').findall(string)  # 分割为64位一组
    M1 = ''
    for subStr in map(lambda str: DES(key, str, DECODE), groups):
        M1 += ''.join(subStr)

    # 将解密后的明文还原为原来的文本
    text = binaryArray2Str(M1, left)
    return text


def encodeFiles(pathname: str, fileObj: dict,
                key: str = '0001001100110100010101110111100110011011101111001101111111110001') -> dict:
    """
    返回一棵树，{name:string, children: [{name:string, children:array, C:string, left:number}, ...], C:string, left:number}
    :param pathname:要遍历的路径
    :param fileObj:{name:string, children:array, C:string, left: number}
    :param key:密匙
    :return:路径描述树
    """
    fileObj['name'] = pathname
    fileObj['children'] = []

    if os.path.isdir(pathname):
        # 文件夹类型
        for name in os.listdir(pathname):
            subFileObj = {}
            encodeFiles(pathname + '/' + name, subFileObj)
            fileObj['children'].append(subFileObj)
    elif os.path.isfile(pathname):
        # 文件类型
        (C, left) = encodeFile(pathname, key)
        fileObj['C'] = C
        fileObj['left'] = left
        return fileObj


def decodeFiles(fileObj: dict, key: str = '0001001100110100010101110111100110011011101111001101111111110001'):
    """
    传入一个JSON解析后的对象，递归还原文件和文件夹
    :param fileObj:文件描述对象，是一棵树, {name:string, children: [{name:string, children:array, C:string, left:number}, ...], C:string, left:number}
    :param key:密匙
    :return:
    """
    if len(fileObj['children']) == 0:
        # 文件类型
        startTime = time.time()
        name = fileObj['name']
        print('正在解密{}... '.format(name), end='')

        left = fileObj['left']
        C = fileObj['C']
        text = decodeText(C, left, key)
        with open(name, 'wb') as f:
            f.write(text)
            endTime = time.time()
            print('耗时{}s!'.format(endTime - startTime))
    else:
        # 文件夹类型
        name = fileObj['name']
        os.makedirs(name)
        # 递归
        for child in fileObj['children']:
            decodeFiles(child, key)


def desEncode(pathname: str, key: str = '0001001100110100010101110111100110011011101111001101111111110001'):
    """
    传入一个文件路径或文件夹路径（当前目录中的路径），
    当前目录中会产生三个pathname.bak, pathname.dat, pathname.dir文件
    :param pathname:被加密的文件路径或文件夹路径
    :param key:密匙, 64位01字符串
    :return:
    """
    obj = {}
    encodeFiles(pathname, obj, key)
    with shelve.open(pathname + '.db') as f:
        f['obj'] = obj


def desDecode(pathname: str, key: str = '0001001100110100010101110111100110011011101111001101111111110001'):
    """
    给一个.db文件，将它还原
    :param pathname: 给出.db文件的路径来解密
    :param key:密匙
    :return:
    """
    with shelve.open(pathname) as f:
        decodeFiles(f['obj'], key)
