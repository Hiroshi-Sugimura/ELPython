#!/usr/bin/python3
"""!
@file PDCEDT.py
@brief ECHONET Liteフレームや、機器オブジェクトのPDCEDT部分
@author SUGIMURA Hiroshi, Kanagawa Institute of Technology
@date 2023年度
@details EDTをPDCと結びつけて管理することを主とする
"""
import platform
import os
env = '' # マイコンやOS

if hasattr(os, 'name'):
    env = platform.system() # Windows, Linux, Darwin
elif hasattr(os, 'uname'):
    env = os.uname().sysname # esp32, rp2
else:
    env = 'Windows'  # 何にもわからなければWindowsとするけど、多分ここには来ない

from copy import deepcopy # パッケージマネージャからcopy @ micropython-libをインストールする

class PDCEDT():
    """!
    @brief PDCEDTクラス
    @details EDTをPDCと結びつけて管理することを主とする
    """
    def __init__(self, obj = None):
        """!
        @brief コンストラクタ
        @param obj (PDCEDT | list[int]) = None
        """
        self.pdc = 0 # @var pdc
        self.edt = []
        self.length = 1
        if obj == None:
            self.pdc = 0
            self.edt = []
            self.length = 1
        elif type(obj) is PDCEDT:
            self.pdc = obj.pdc
            self.edt = deepcopy(obj.edt)
            self.length = obj.length
        elif type(obj) is list and len(obj) != 0:
            self.pdc = obj[0]
            if self.pdc == 0:
                self.edt = []
            else:
                self.edt = obj[1:]
            self.length = len(obj)
        else:
            self.pdc = 0
            self.edt = []
            self.length = 1

    def __del__(self):
        """!
        @brief デストラクタ
        """
        #print("__del__")

    def __eq__(self, other) -> bool:
        """!
        @brief 等価比較演算子
        @param other (PDCEDT)
        @return bool
        """
        # ==
        # print("__eq__")
        if not isinstance(other, PDCEDT):
            return NotImplemented
        return (self.pdc == other.pdc) and (self.edt == other.edt) and (self.length == other.length)

    def setEDT(self, edt):
        """!
        @brief EDTを指定して格納、PDCは自動計算
        @param edt (list[int])
        """
        self.pdc = len(edt)
        if self.pdc == 0:
            self.edt = []
        else:
            self.edt = edt
        self.length = len(edt)+1

    def getString(self) -> str:
        """!
        @brief PDCEDTの文字列を返す
        @return str
        """
        if self.edt==None:
            return '00'
        else:
            if env == 'esp32' or env == 'rp2':
                hexArr = ['{:02X}'.format(i) for i in self.edt]
                return '{:02X}'.format(self.pdc) + "".join(hexArr).lower()
            else:
                hexArr = [format(i,'02x') for i in self.edt]
                return format(self.pdc,'02x') + "".join(hexArr).lower()

    def println(self):
        """!
        @brief 現在の格納データを標準出力する
        """
        if len(self.edt) == 0:
            #print("PDC:", format(self.pdc,'02x'), ", EDT: []" )
            print("PDC:", '{:02X}'.format(self.pdc), ", EDT: []" )
        else:
            # h = [format(i,'02X') for i in self.edt]
            h = ['{:02X}'.format(i) for i in self.edt]
            # print("PDC:", format(self.pdc,'02x'), ", EDT:", ",".join(h) )
            print("PDC:", '{:02X}'.format(self.pdc), ", EDT:", ",".join(h) )

    def printString(self) -> str:
        """!
        @brief 現在の格納データを文字列出力する
        @return str
        """
        s = ""
        if len(self.edt) == 0:
            # s = "PDC:" + format(self.pdc,'02x') +", EDT: []"
            s = "PDC:" + '{:02X}'.format(self.pdc) +", EDT: []"
        else:
            # h = [format(i,'02x') for i in self.edt]
            h = ['{:02X}'.format(i) for i in self.edt]
            # s = "PDC:" + format(self.pdc,'02x') + ", EDT:" + (",".join(h))
            s = "PDC:" + '{:02X}'.format(self.pdc) + ", EDT:" + (",".join(h))
        return s


if __name__ == '__main__':
    print("===== PDCEDT.py 単体テスト")
    print("-- t1")
    test1 = PDCEDT()
    test1.println()
    print("-- t2")
    test2 = PDCEDT([1, 0x80])
    test2.println()
    test22 = PDCEDT([1, 0x80])
    print(test2==test1)
    print(test2==test22)
    print("-- t3")
    test3 = test22
    test3.println()
    test3.setEDT([0x80,0x81])
    test3.println()
    print("test3.pdc:", test3.pdc)
    print("test3.edt:", test3.edt)
    print(test3.getString())
    print(test3.printString())
    print("-- t4")
    test4 = PDCEDT([0, 0x00])
    test4.println()
    test4.setEDT([0x30])
    test4.println()
