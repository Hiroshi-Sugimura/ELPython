# EchonetLite.py マニュアル

## 使用方法

1. EchonetLiteフォルダをプロジェクトフォルダに配置
2. 必要なライブラリをインストールする
```
pip install netifaces2
```
3. メインプログラムで下記の様にインポートする
```
from EchonetLite import EchonetLite, PDCEDT, ELOBJ
```
4. 下記サンプルをベースに書き換える
```sample
from EchonetLite import EchonetLite, PDCEDT, ELOBJ

# SET系命令を処理する、デバイス系ではこれにまじめに対応する
# SETI, SETC, SETGET
def userSetFunc( ip, tid, seoj, deoj, esv, opc, epc, pdcedt):
    print("---------- Set")
    print("from:", ip)
    print("eldata:", "TID:", tid, "SEOJ:", seoj, "DEOJ:", deoj, "ESV:", esv, "OPC:", opc, "EPC:", epc, pdcedt.printString())
    return True

# GET系命令を処理する、ほとんど処理する必要はない
# GET, INF_REQ, INFC, SETGET
def userGetFunc( ip, tid, seoj, deoj, esv, opc, epc, pdcedt):
    print("---------- Set")
    print("from:", ip)
    print("eldata:", "TID:", tid, "SEOJ:", seoj, "DEOJ:", deoj, "ESV:", esv, "OPC:", opc, "EPC:", epc, pdcedt.printString())
    return True

# INF系、GETの返信を処理する、コントローラ系ではここから機器情報を収集する
# INF, SETI_SNA, SETC_SNA, GET_SNA, INF_SNA, SET_RES, GET_RES, INFC_RES, SETGET_SNA, SETGET_RES
def userInfFunc( ip, tid, seoj, deoj, esv, opc, epc, pdcedt):
    print("---------- Set")
    print("from:", ip)
    print("eldata:", "TID:", tid, "SEOJ:", seoj, "DEOJ:", deoj, "ESV:", esv, "OPC:", opc, "EPC:", epc, pdcedt.printString())
    return True



# ECHONET Liteのオブジェクトを準備
el = EchonetLite([[0x05,0xff,0x01]])

# ECHONET Liteの命令処理を登録し、受信開始
el.begin(userSetFunc, userGetFunc, userInfFunc)

# 一般照明の電源状態を定期的に確認
while True:
    el.sendMultiOPC1String('05ff01', '029001', '62', '80', '00')
    now = datetime.datetime.now()
    print(now.strftime("%Y年%m月%d日 %H時%M分%S秒"), "に送信")
    time.sleep(60) # 1 min
```
5. より詳細なサンプルはELWeb、SSNGpyを参考にしてください
