#!/usr/bin/python3

import sys
import os
import signal
import time
import datetime
from EchonetLite import EchonetLite, PDCEDT

args = sys.argv

def userSetFunc( ip, tid, seoj, deoj, esv, opc, epc, pdcedt:PDCEDT):
    """!
    @brief SET系（SETI、SETC、SETGET）命令を受け取った時に処理するものがあればここに記述
    @param ip (str)
    @param tid (list[int])
    @param seoj (list[int])
    @param deoj (list[int])
    @param esv (int)
    @param opc (int)
    @param epc (int)
    @param pdcedt (PDCEDT)
    @return bool 成功=True, 失敗=False、プロパティがあればTrueにする
    @note SET必要な処理を記述する。プロパティの変化があれば、正しくデバイス情報をUpdateしておくことが重要
    """
    print("---------- Set")
    print("| from:", ip)
    print("| TID:", el.getHexString(tid), "SEOJ:", el.getHexString(seoj), "DEOJ:", el.getHexString(deoj), "ESV:", el.getHexString(esv), "OPC:", el.getHexString(opc), "EPC:", el.getHexString(epc), pdcedt.printString())

    if esv == EchonetLite.SETI or esv == EchonetLite.SETC:
        if epc == 0x80: # power
            if pdcedt.edt == [0x30]:
                print('Power ON')
                el.update(deoj, epc, pdcedt.edt)
            elif pdcedt.edt == [0x31]:
                print('Power OFF')
                el.update(deoj, epc, pdcedt.edt)
        elif epc == 0x81: # 設置場所
            el.update(deoj, epc, pdcedt.edt)
        elif epc == 0x88: # エラー情報
            el.update(deoj, esv, pdcedt.edt)
        else:
            return False
    return True

def userGetFunc( ip, tid, seoj, deoj, esv, opc, epc, pdcedt):
    """!
    @brief GET系（GET、SETGET、INFC）命令を受け取った時に処理するものがあればここに記述
    @param ip (str)
    @param tid (list[int])
    @param seoj (list[int])
    @param deoj (list[int])
    @param esv (int)
    @param opc (int)
    @param epc (int)
    @param pdcedt (PDCEDT)
    @return bool 成功=True, 失敗=False、プロパティがあればTrueにする
    @note GET命令に関しては基本的に内部で処理で返却するので、一般にはここに何も記述しなくてよい。SET命令のときに、正しくデバイス情報をUpdateしておくことが重要
    """
    print("---------- Get")
    print("| from:", ip)
    print("| TID:", el.getHexString(tid), "SEOJ:", el.getHexString(seoj), "DEOJ:", el.getHexString(deoj), "ESV:", el.getHexString(esv), "OPC:", el.getHexString(opc), "EPC:", el.getHexString(epc), pdcedt.printString())
    return True

def userInfFunc( ip, tid, seoj, deoj, esv, opc, epc, pdcedt):
    """!
    @brief INF系命令（INF、*_RES、*_SNA）を受け取った時に処理するものがあればここに記述
    @param ip (str)
    @param tid (list[int])
    @param seoj (list[int])
    @param deoj (list[int])
    @param esv (int)
    @param opc (int)
    @param epc (int)
    @param pdcedt (PDCEDT)
    @return bool 成功=True, 失敗=False、プロパティがあればTrueにする
    @note INF命令に関しては一般に、デバイス系では無視、コントローラー系では情報保持をすると思われる。
    """
    print("---------- INF, RES, SNA")
    print("| from:", ip)
    print("| TID:", el.getHexString(tid), "SEOJ:", el.getHexString(seoj), "DEOJ:", el.getHexString(deoj), "ESV:", el.getHexString(esv), "OPC:", el.getHexString(opc), "EPC:", el.getHexString(epc), pdcedt.printString())
    return True

# el = EchonetLite([[0x02,0x90,0x01]], options={"debug":True}) # General Lighting, debug on
el = EchonetLite([[0x02,0x90,0x01]]) # General Lighting, no debug
el.update([0x02,0x90,0x01], 0x9d, [0x80, 0xd6])
el.update([0x02,0x90,0x01], 0x9e, [0x80, 0xb0, 0xb6, 0xc0])
el.update([0x02,0x90,0x01], 0x9f, [0x80, 0x81, 0x82, 0x83, 0x88, 0x8a, 0x9d, 0x9e, 0x9f])
#el.println()

el.begin(userSetFunc, userGetFunc, userInfFunc)

def loop():
    while True:
        # el.sendMultiOPC1('05ff01', '029001', '62', '80', '00')
        now = datetime.datetime.now()
        # print(frame)
        # print(now.strftime("%Y年%m月%d日 %H時%M分%S秒"), "に送信されました。") # フォーマットして出力
        time.sleep(60) # 1 min


def handler(signum, frame):
    # 何らかの処理
    del el
    sys.exit(0)

signal.signal(signal.SIGFPE, handler)

try:
    loop()
except:
    print("except -> exit")
    os._exit(0) # sys.exitではwindowsの受信ソケットが解放されないので仕方なく
