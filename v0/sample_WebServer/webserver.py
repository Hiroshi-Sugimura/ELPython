#!/usr/bin/python3

import os
import sys
import urllib.parse
import html
import threading
import time
import datetime
import json

from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
from http import HTTPStatus

from EchonetLite import EchonetLite, PDCEDT


args = sys.argv

# WebServer
PORT = 8000


# EchonetLite
facilities:dict[str, dict[str, dict[str, str]]] = {} # ECHONET Liteネットワーク機器


# EchonetLite
def getFacilitiesJson(f):
    if len(f) == 0:
        return ""
    return json.dumps(f, ensure_ascii=False, indent=2)


def userSetFunc( ip, tid, seoj, deoj, esv, opc, epc, pdcedt):
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
    #print("---------- Set")
    #print("from:", ip)
    #print("TID:", el.getHexString(tid), "SEOJ:", el.getHexString(seoj), "DEOJ:", el.getHexString(deoj), "ESV:", el.getHexString(esv), "OPC:", el.getHexString(opc), "EPC:", el.getHexString(epc), pdcedt.printString())

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
    #print("---------- Get")
    #print("from:", ip)
    #print("TID:", el.getHexString(tid), "SEOJ:", el.getHexString(seoj), "DEOJ:", el.getHexString(deoj), "ESV:", el.getHexString(esv), "OPC:", el.getHexString(opc), "EPC:", el.getHexString(epc), pdcedt.printString())
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
    #print("---------- INF, RES, SNA")
    #print("from:", ip)
    #print("TID:", el.getHexString(tid), "SEOJ:", el.getHexString(seoj), "DEOJ:", el.getHexString(deoj), "ESV:", el.getHexString(esv), "OPC:", el.getHexString(opc), "EPC:", el.getHexString(epc), pdcedt.printString())
    
    # 受信データをfacilitiesに記憶しておく
    seoj_s = el.getHexString(seoj)
    epc_s = el.getHexString(epc)
    pdc_s = el.getHexString(pdcedt.pdc)
    edt_s = el.getHexString(pdcedt.edt)
    
    if facilities.get(ip) == None:
        facilities[ip] = {}
    if facilities[ip].get(seoj_s) == None:
        facilities[ip][seoj_s] = {}
    if facilities[ip][seoj_s].get(epc_s) == None:
        facilities[ip][seoj_s][epc_s] = {}
    facilities[ip][seoj_s][epc_s] = dict(pdc=pdc_s, edt=edt_s)

    if esv == EchonetLite.GET_RES or esv == EchonetLite.INF:
        if epc == 0xd6: # インスタンスリスト
            # print("instance list[s]")
            # pdcedt.println()
            index = 0
            count = pdcedt.edt[index]
            index += 1
            for _ in range(0, count):
                el.sendGetPropertyMap(ip, pdcedt.edt[ index: index+3])
                index += 3
        elif epc == 0x9f: # Getプロパティマップ
            #print("get property map")
            props = el.parsePropertyMap(pdcedt)
            opc = len(props)
            epcs = {}
            v_len = 0
            for v in props:
                if v == 0x9f: # 9fを受け取って9fを聞きに行くと無限ループなので聞かない
                    continue
                epcs[v] = PDCEDT([0])
                v_len += 1
            el.sendDetails(ip, el.getTidString(), el.EOJ_Controller, seoj, el.GET, v_len, epcs)
    return True


# Web Server
class ELHttpRequestHandler(BaseHTTPRequestHandler):
    server_version = "HTTP Stub/0.1"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def do_GET(self):
        enc = sys.getfilesystemencoding()
        title = "ECHONET Lite Controller, Facilities data"
        jsonData = getFacilitiesJson(facilities)

        r = []
        r.append('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" '
                 '"http://www.w3.org/TR/html4/strict.dtd">')
        r.append('<html>\n<head>')
        r.append('<meta http-equiv="Content-Type" '
                 'content="text/html; charset=%s">' % enc)
        r.append('<title>%s</title>\n</head>' % title)
        r.append('<body>\n<h1>%s</h1>' % title)
        r.append('<hr>\n<pre>')
        r.append(jsonData)
        r.append('</pre>\n<hr>\n</body>\n</html>\n')
        encoded = '\n'.join(r).encode(enc, 'surrogateescape')

        self.send_response(HTTPStatus.OK)
        self.send_header("Content-type", "text/html; charset=%s" % enc)
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()

        self.wfile.write(encoded)     


#====================================================================================================
# 開始

# Web
handler = ELHttpRequestHandler
httpd = HTTPServer(('',PORT),handler)
#httpd.serve_forever()
server_thread = threading.Thread(target=httpd.serve_forever) # スレッドで動かす
server_thread.start()
print('http://localhost:8000')

# EL
el = EchonetLite([[0x05,0xff,0x01]]) # Controller
el.update([0x05,0xff,0x01], 0x9d, [0x80, 0xd6])
el.update([0x05,0xff,0x01], 0x9e, [0x80])
el.update([0x05,0xff,0x01], 0x9f, [0x80, 0x81, 0x82, 0x83, 0x88, 0x8a, 0x9d, 0x9e, 0x9f])
el.begin(userSetFunc, userGetFunc, userInfFunc)
el.sendMultiOPC1( el.EOJ_NodeProfile, el.EOJ_NodeProfile, el.GET, 0xd6, PDCEDT([0])) # インスタンスリスト取得

while True:
    el.sendMultiOPC1( el.EOJ_Controller, '013000', '62', '80', '00') # ホームエアコン
    el.sendMultiOPC1( el.EOJ_Controller, '013500', '62', '80', '00') # 空気清浄機
    el.sendMultiOPC1( el.EOJ_Controller, '015600', '62', '80', '00') # 業務用パッケージエアコン室内機
    el.sendMultiOPC1( el.EOJ_Controller, '015700', '62', '80', '00') # 業務用パッケージエアコン室外機
    el.sendMultiOPC1( el.EOJ_Controller, '029000', '62', '80', '00') # 一般照明
    now = datetime.datetime.now()
    print("Got data at", now.strftime("%Y年%m月%d日 %H時%M分%S秒")) # フォーマットして出力
    #print(getFacilitiesJson(facilities))
    time.sleep(60) # 1 min
