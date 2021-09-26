from workingMode import ENCODE, DECODE
from tables.ipReplacementTable import ipReplacementTable
from tables.keyReplacementTable import keyReplacementTable
from tables.shiftLeftTable import shiftLeftTable
from tables.compressTable import compressTable
from tables.expansionTable import expansionTable
from utils import binaryArrayXOR, sliceXORed, strTransformBySBox
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
    finalTransformed = list(map(lambda index: RiLi[index-1], finalTable))
    # 验证加密
    # print(''.join(finalTransformed)=='1000010111101000000100110101010000001111000010101011010000000101')
    # 验证解密
    # print(''.join(finalTransformed)=='0000000100100011010001010110011110001001101010111100110111101111')
    return finalTransformed

if __name__ == '__main__':
    DES('0001001100110100010101110111100110011011101111001101111111110001',
        '0000000100100011010001010110011110001001101010111100110111101111', ENCODE)
    # DES('0001001100110100010101110111100110011011101111001101111111110001',
    #     '1000010111101000000100110101010000001111000010101011010000000101', DECODE)