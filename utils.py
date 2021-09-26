import re
from tables.sBox import sBox


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


def str2binaryArray(string: str, encoding: str) -> list:
    """
    将任意字符串转换为一个二进制字符数组，长度大于等于8且无上限
    :param string:被解析的字符串
    :param encoding:编码方式，默认为utf-8
    :return:返回值为一个字符串数组，其中每一个字符串都是长度为8的0/1字符串
    """
    bytes = string.encode(encoding)
    binaryStrs = [bin(b)[2:] for b in bytes]

    return list(map(lambda b: '0' * (8 - len(b)) + b, binaryStrs))


def binaryArray2Str(string: str, encoding: str = 'utf-8') -> str:
    """
    将一个0/1字符串转换为它原本的文本
    :param string:0/1字符串
    :param encoding:编码方式，默认为utf-8
    :return:
    """
    groups = re.compile(r'[01]{8}').findall(string)  # 8位一组
    return bytes([int(str, 2) for str in groups]).decode(encoding)
