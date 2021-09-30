# py-des

#### 介绍
python实现DES算法加密64位二进制01字符串（DES函数），
也可加密和解密文件和文件夹（desEncode和desDecode）

#### 使用说明
utils.py中有三个函数
```python
DES(key: str, data: str, mode: str = ENCODE) -> list

desEncode(pathname: str, key: str)

desDecode(pathname: str, key: str)
```
