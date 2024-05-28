#!/usr/bin/python3
"""!
@file EchonetLite.py
@brief ECHONET Lite送受信処理を管理する、プロファイルオブジェクトや機器オブジェクトを管理する
@author SUGIMURA Hiroshi, Kanagawa Institute of Technology
@date 2023年度
@details UDP socketやELOBJを管理することを主とする
"""

import platform
import socket
import binascii
if platform.system() == 'Linux':
    import ipget  #  インストール必要, for Linux
import threading
import struct
import uuid
import re


if __name__ == '__main__':
    from PDCEDT import PDCEDT
    from ELOBJ import ELOBJ
else:
    from EchonetLite.PDCEDT import PDCEDT
    from EchonetLite.ELOBJ import ELOBJ


class EchonetLite():
    """!
    @brief ECHONET Lite通信クラス
    @note 受信ポート3610を占有するのでPCで一つだけインスタンス化して利用する。
    細かいことを言えばbeginを実施しなければ受信開始しないので送信だけはできるかも。
    """
    MINIMUM_FRAME = 13 # ECHONET Lite通信の最小フレームサイズ
    MULTICAST_GROUP='224.0.23.0' # マルチキャストアドレス
    ECHONETport = 3610 # ECHONET Liteの規格port
    BUFFER_SIZE = 1500 # 受信バッファサイズ 、UDP なので1500あればよいでしょう
    EHD1 = 0			# EHD1
    EHD2 = 1			# EHD2
    TID = 2			    # TID 2 byte
    SEOJ = 4			# SEOJ 3 byte
    DEOJ = 7			# DEOJ 3 byte
    ESV = 10			# ESV
    OPC = 11			# OPC
    EPC = 12			# EPC
    PDC = 13			# PDC
    EDT = 14			# EDT n byte
    SETI_SNA = 0x50	# SETI_SNA
    SETC_SNA = 0x51	# SETC_SNA
    GET_SNA = 0x52		# GET_SNA
    INF_SNA = 0x53		# INF_SNA
    SETGET_SNA = 0x5e	# SETGET_SNA
    SETI = 0x60		# SETI
    SETC = 0x61		# SETC
    GET = 0x62			# GET
    INF_REQ = 0x63		# INF_REQ
    SETGET = 0x6e		# SETGET
    SET_RES = 0x71		# SET_RES
    GET_RES = 0x72		# GET_RES
    INF = 0x73			# INF
    INFC = 0x74		# INFC
    INFC_RES = 0x7a	# INFC_RES
    SETGET_RES = 0x7e	# SETGET_RES
    EOJ_Controller = [0x05, 0xff, 0x01] # EOJ:Controller
    EOJ_NodeProfile = [0x0e, 0xf0, 0x01] # EOJ:NodeProfileObject

    #  コンストラクタ
    def __init__(self, eojs = None, options = None):
        """!
        @brief コンストラクタ
        @param eojs eoj[3]の配列、指定がなければコントローラとする
        @param options デフォルトNone, future reserved
        @note eojsは一つの場合でも次のように配列として定義する [ EchonetLite.EOJ_Controller ]
        """
        # optionsを内部に保持
        self.debug = False
        if options:
            if options.debug == True:
                self.debug = True

        # ip 設定
        if platform.system() == 'Linux': # for Linux
            localIP = ipget.ipget()
            # print(localIP.ipaddr("wlan0"))
            self.LOCAL_ADDR = str(localIP.ipaddr("wlan0")).split('/')[0] # for Linux
        elif platform.system() == 'Darwin': # mac
            self.LOCAL_ADDR = socket.gethostbyname(socket.gethostname()) # for mac
        else:
            self.LOCAL_ADDR = socket.gethostbyname(socket.gethostname()) # for windows

        #print("Local IP:", self.LOCAL_ADDR) # debug
        self.mac = self.getHwAddr()
        self.tid = [0,0]
        self.devices = {}
        self.userSetFunc = self.dummyFuncion
        self.userGetFunc = self.dummyFuncion
        self.userInfFunc = self.dummyFuncion
        if eojs == None:
            eojs = [ EchonetLite.EOJ_Controller ]
        self.eojs = eojs
        self.instanceNumber = len(eojs)
        k = "" # devices index = key
        # device object
        for eoj in eojs:
            k = self.getHexString(eoj)  # eoj:str
            self.devices[k] = ELOBJ()
            self.devices[k].SetEDT(0x80, [0x30])            # power
            self.devices[k].SetEDT(0x81, [0x00])            # position
            self.devices[k].SetEDT(0x82, [0x00, 0x00, 0x52, 0x01]) # release R, rev.1
            self.devices[k].SetEDT(0x83, [0xfe, 0x00, 0x00, 0x77, self.mac[0], self.mac[1], self.mac[2], self.mac[3], self.mac[4], self.mac[5], eoj[0], eoj[1], eoj[2], 0x00, 0x00, 0x00, 0x00]) # identification number
            self.devices[k].SetEDT(0x88, [0x42])             # error status
            self.devices[k].SetEDT(0x8a, [0x00, 0x00, 0x77]) # maker KAIT
            self.devices[k].SetMyPropertyMap(0x9d, [0x80, 0xd6, 0x88])    # inf property map
            self.devices[k].SetMyPropertyMap(0x9e, [0x80, 0x81])       # set property map
            self.devices[k].SetMyPropertyMap(0x9f, [0x80, 0x81, 0x82, 0x83, 0x88, 0x8a, 0x9d, 0x9e, 0x9f]) # get property map
        # node profile
        k = '0ef001'
        self.devices[k] = ELOBJ()
        self.devices[k].SetEDT(0x80, [0x30])					# power
        self.devices[k].SetEDT(0x82, [0x01, 0x0d, 0x01, 0x00]) # Ver 1.13 (type 1)
        # [0] = 0xfe, [1-3] = メーカコード３バイト が決まり
        self.devices[k].SetEDT(0x83, [0xfe, 0x00, 0x00, 0x77, self.mac[0], self.mac[1], self.mac[2], self.mac[3], self.mac[4], self.mac[5], 0x0e, 0xf0, 0x01, 0x00, 0x00, 0x00, 0x00]) # identification number
        self.devices[k].SetEDT(0x88, [0x42])			 # error status
        self.devices[k].SetEDT(0x8a, [0x00, 0x00, 0x77]) # maker KAIT
        self.devices[k].SetEDT(0xbf, [0x00, 0x00])       # unique identifier data

        devList = self.getInstanceList(eojs)
        classList = self.getClassList(eojs)

        self.devices[k].SetEDT(0xd3, [0x00, 0x00, devList[0]])       # total instance number、デバイスオブジェクトの数
        self.devices[k].SetEDT(0xd4, [0x00, classList[0]])	         # total class number、デバイスクラス＋ノードプロファイルクラス
        self.devices[k].SetEDT(0xd5, devList)            # obj list
        self.devices[k].SetEDT(0xd6, devList)            # obj list
        self.devices[k].SetEDT(0xd7, classList)          # class list

        self.devices[k].SetMyPropertyMap(0x9d, [0x80, 0xd5])																	# inf property map
        self.devices[k].SetMyPropertyMap(0x9e, [0x80])																			# set property map
        self.devices[k].SetMyPropertyMap(0x9f, [0x80, 0x82, 0x83, 0x88, 0x8a, 0x9d, 0x9e, 0x9f, 0xd3, 0xd4, 0xd5, 0xd6, 0xd7]) # get property map
        # 受信ソケットの準備
        self.rsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.group = socket.inet_aton(EchonetLite.MULTICAST_GROUP)
        self.mreq = struct.pack('4sL', self.group, socket.INADDR_ANY)
        self.rsock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, self.mreq)
        self.rsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    #  デストラクタ
    def __del__(self):
        """!
        @brief デストラクタ
        """
        #  受信設定
        self.rsock.close()

    def dummyFuncion(self, ip, tid, seoj, deoj, esv, opc, epc, pdcedt):
        """!
        @brief ユーザのコールバックが指定されない場合のダミー関数
        @param ip (str)
        @param tid list[int]
        @param seoj list[int]
        @param deoj list[int]
        @param esv int
        @param opc int
        @param epc int
        @param pdcedt PDCEDT
        @return bool True固定
        """
        if self.debug:
            print('dummyFunction ', ip, tid, seoj, deoj, esv, opc, epc, pdcedt.printString())
        return True


    def begin(self, sfunc, gfunc=None, ifunc=None):
        """!
        @brief 受信開始
        @param sfunc Setの時に呼ばれる関数、設定が必須
        @param gfunc Getの時に呼ばれる関数、設定しないならNoneでよい。省略すればNone
        @param ifunc 通知関係を受信した時に呼ばれる関数、設定しないならNoneでよい。省略すればNone
        """
        if sfunc != None:
            self.userSetFunc = sfunc
        if gfunc != None:
            self.userGetFunc = gfunc
        if ifunc != None:
            self.userInfFunc = ifunc
        # 受信設定
        self.rsock.bind(('', self.ECHONETport))
        self.rsock.settimeout(1)
        def recv():
            while True:
                try:
                    data, ip = self.rsock.recvfrom(EchonetLite.BUFFER_SIZE)
                    # bytesを16進数文字列に変換する
                    self.returner(ip[0], list(data))
                except socket.timeout:
                    continue
        self.thread = threading.Thread(target=recv, args=())
        self.thread.start() #  受信スレッド開始
        # インスタンスリスト通知 D5
        seoj = self.EOJ_NodeProfile
        deoj = self.EOJ_NodeProfile
        if self.devices['0ef001'][0x80] != None:
            self.sendMultiOPC1(seoj, deoj, self.INF, 0x80, self.devices['0ef001'][0x80]) # ON通知
        if self.devices['0ef001'][0xd5] != None:
            self.sendMultiOPC1(seoj, deoj, self.INF, 0xd5, self.devices['0ef001'][0xd5]) # オブジェクトリスト通知


    def update(self, obj, epc, edt):
        """!
        @brief 保持しているオブジェクトのEPCに対応するEDTを更新する。更新した結果、INFプロパティならマルチキャスト送信もする
        @param obj list[int]|str
        @param epc int
        @param edt list[int]
        """
        if type(obj) is list:
            obj = self.getHexString(obj)

        if epc == 0x9d or epc == 0x9e or epc == 0x9f:
            self.devices[obj].SetMyPropertyMap(epc, edt)
        else:
            self.devices[obj].SetEDT(epc, edt)
            self.checkInfAndSend(obj, epc)


    #  送信
    def send(self, ip, message):
        """!
        @brief ECHOENT Lite のデータ送信
        @param buffer (bytes|list[int]|str)
        """
        if type(message) is list:
            buffer = bytes(message)
        elif type(message) is str:
            buffer = binascii.unhexlify(message)
        elif type(message) is bytes:
            buffer = message
        else:
            return

        ssock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ssock.sendto(buffer, (ip, self.ECHONETport))
        ssock.close()


    def sendOPC1TID(self, ip, tid, seoj, deoj, esv, epc, pdcedt):
        """!
        @brief OPCが1としてユニキャスト、TIDあり
        @param ip (str)
        @param tid (list[int]|str)
        @param seoj (list[int]|str)
        @param deoj (list[int]|str)
        @param esv (int|str)
        @param epc (int|str)
        @param pdcedt (PDCEDT|str)
        @note detailsはkey=epc:int、value=PDCEDT()のdict
        """
        if type(tid) is list:
            tid = self.getHexString(tid)

        if type(seoj) is list:
            seoj = self.getHexString(seoj)

        if type(deoj) is list:
            deoj = self.getHexString(deoj)

        if type(esv) is int:
            esv = self.getHexString(esv)

        if type(epc) is int:
            epc = self.getHexString(epc)

        if type(pdcedt) is PDCEDT:
            pdcedt = pdcedt.getString()
        elif type(pdcedt) is list:
            pdcedt = self.getHexString(pdcedt)

        smsg = '1081' + tid + seoj + deoj + esv + '01' + epc + pdcedt
        self.send(ip, smsg)

    def sendOPC1(self, ip, seoj, deoj, esv, epc, pdcedt):
        """!
        @brief OPCが1としてユニキャスト、TID自動
        @param ip (str)
        @param seoj (list[int]|str)
        @param deoj (list[int]|str)
        @param esv (int|str)
        @param epc (int|str)
        @param pdcedt (PDCEDT|str)
        @note detailsはkey=epc:int、value=PDCEDT()のdict
        """
        self.sendOPC1TID(ip, self.getTidString(), seoj, deoj, esv, epc, pdcedt)

    def sendDetails(self, ip, tid, seoj, deoj, esv, opc, details):
        """!
        @brief detailsを指定して送信
        @param ip str
        @param tid (list[int]|str)
        @param seoj (list[int]|str)
        @param deoj (list[int]|str)
        @param esv (int|str)
        @param opc (int|str)
        @param details (Dict[int,PDCEDT])
        @note detailsはkey=epc:int、value=PDCEDT()のdict
        """
        if type(tid) == list:
            tid = self.getHexString(tid)

        if type(seoj) == list:
            seoj = self.getHexString(seoj)

        if type(deoj) == list:
            deoj = self.getHexString(deoj)

        if type(esv) == int:
            esv = self.getHexString(esv)

        if type(opc) == int:
            opc = self.getHexString(opc)

        smsg = '1081' + tid + seoj + deoj + esv + opc

        for epc in details:
            smsg += format(epc,'02x') + details[epc].getString()

        if ip == self.MULTICAST_GROUP:
            self.sendMulti(smsg)
        else:
            self.send(ip, smsg)

    def sendMulti(self, message):
        """!
        @brief マルチキャストの送信
        @param message (bytes | list[int] | str)
        """
        if type(message) == list:
            buffer = bytes(message)
        elif type(message) == str:
            buffer = binascii.unhexlify(message)
        elif type(message) == bytes:
            buffer = message
        else:
            return

        ssock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ssock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(self.LOCAL_ADDR))
        ssock.sendto(buffer, (EchonetLite.MULTICAST_GROUP, EchonetLite.ECHONETport))
        ssock.close()


    def sendMultiOPC1TID(self, tid, seoj, deoj, esv, epc, pdcedt):
        """!
        @brief OPCが1としてマルチキャスト、TID指定
        @param ip (str)
        @param tid (list[int]|str)
        @param seoj (list[int]|str)
        @param deoj (list[int]|str)
        @param esv (int|str)
        @param epc (int|str)
        @param pdcedt (PDCEDT|str)
        @note detailsはkey=epc:int、value=PDCEDT()のdict
        """
        if type(tid) == list:
            tid = self.getHexString(tid)

        if type(seoj) == list:
            seoj = self.getHexString(seoj)

        if type(deoj) == list:
            deoj = self.getHexString(deoj)

        if type(esv) == int:
            esv = self.getHexString(esv)

        if type(epc) == int:
            epc = self.getHexString(epc)

        if type(pdcedt) == PDCEDT:
            pdcedt = pdcedt.getString()
        elif type(pdcedt) == list:
            pdcedt = self.getHexString(pdcedt)

        smsg = '1081' + tid + seoj + deoj + esv + '01' + epc + pdcedt
        self.sendMulti(smsg)


    def sendMultiOPC1(self, seoj, deoj, esv, epc, pdcedt):
        """!
        @brief OPCが1としてマルチキャスト、TID自動
        @param ip (str)
        @param seoj (list[int]|str)
        @param deoj (list[int]|str)
        @param esv (int|str)
        @param epc (int|str)
        @param pdcedt (PDCEDT|str)
        @note detailsはkey=epc:int、value=PDCEDT()のdict
        """
        tid = self.getTidString()
        self.tidAutoIncrement()
        self.sendMultiOPC1TID( tid, seoj, deoj, esv, epc, pdcedt)

    def sendGetPropertyMap(self, ip, eoj):
        """!
        @brief 指定IPの指定EOJのもつINF、SET、GETプロパティマップを取得する
        @param ip (str)
        @param eoj (list[int]|str)
        """
        # プロファイルオブジェクトのときはプロパティマップももらうけど，識別番号ももらう
        pdcedts = {}
        if eoj[0:3] == [0x0e,0xf0,0x01]:
            pdcedts[0x83] = PDCEDT([0])
            pdcedts[0x9d] = PDCEDT([0])
            pdcedts[0x9e] = PDCEDT([0])
            pdcedts[0x9f] = PDCEDT([0])
            self.sendDetails( ip, self.getTidString(), EchonetLite.EOJ_NodeProfile, eoj, EchonetLite.GET, 0x04, pdcedts)
        else:
            # デバイスオブジェクト
            pdcedts[0x9d] = PDCEDT([0])
            pdcedts[0x9e] = PDCEDT([0])
            pdcedts[0x9f] = PDCEDT([0])
            self.sendDetails( ip, self.getTidString(), EchonetLite.EOJ_NodeProfile, eoj, EchonetLite.GET, 0x03, pdcedts)
        self.tidAutoIncrement()

    def replyGetDetail(self, ip, tid, seoj, deoj, esv, opc, details):
        """!
        @brief Getに対して複数OPCに対応して返答する内部関数
        @param ip (str)
        @param tid (list[int])
        @param seoj (list[int])
        @param deoj (list[int])
        @param esv (list[int])
        @param opc (int)
        @param details (dict)
        @return bool
        """
        success = True
        rep_details = {}  # 返信用のEPC,PDC,EDT[PDC]をすべて並べる

        for epc in details:
            devProp = self.replyGetDetail_sub(deoj, epc)
            if devProp == None:
                rep_details[epc] = PDCEDT([0]) # GetのエラーはPDC=0
                success = False
            else:
                rep_details[epc] = devProp

        if success == True:
            esv = EchonetLite.GET_RES
        else:
            esv = EchonetLite.GET_SNA

        # SEOJとDEOJが入れ替わる
        self.sendDetails(ip, tid, deoj, seoj, esv, opc, rep_details)
        return success

    def replyGetDetail_sub(self, eoj, epc):
        """!
        @brief EOJとEPCを指定した時、そのプロパティがあるかチェックする内部関数
        @param ip str
        @param seoj list[int]
        @param epc int
        @return PDCEDT | None そのプロパティのPDCEDT、存在しなければNone
        """
        if( eoj==self.EOJ_NodeProfile ):
            return self.devices['0ef001'][epc]
        else:
            for i in range(0, self.instanceNumber):
                if eoj==self.eojs[i]:
                    return self.devices[self.getHexString(eoj)][epc]
            return None


    def replySetDetail(self, ip, tid, seoj, deoj, esv, opc, details):
        """!
        @brief Setに対して複数OPCに対応して返答する内部関数
        @param ip (str)
        @param tid (list[int])
        @param seoj (list[int])
        @param deoj (list[int])
        @param esv (int)
        @param opc (int)
        @param details (dict)
        @return bool
        """
        success = True
        rep_details = {}  # 返信用のEPC,PDC,EDT[PDC]をすべて並べる

        for epc in details:
            devProp = self.replySetDetail_sub(deoj, epc)
            if devProp == None: # プロパティ無し
                rep_details[epc] = details[epc] # Setのエラーは、元データを返却する
                success = False
            else: # プロパティあり
                if self.userSetFunc != None:
                    if self.userSetFunc(ip, tid, seoj, deoj, esv, opc, epc, details[epc] ) == False:
                        success = False
                        rep_details[epc] = details[epc] # Setの失敗は要求の値を返却する
                    else:
                        rep_details[epc] = PDCEDT([0]) # Setの成功はPDC=0

        if success == False and esv == self.SETI:
            esv = EchonetLite.SETI_SNA
        elif success == False and esv == self.SETC:
            esv = EchonetLite.SETC_SNA
        elif success == True and esv == self.SETI:
            # print("SETIの成功は返却しない")
            return success
        else:
            esv = EchonetLite.SET_RES

        # 返信用データはSEOJとDEOJが反転する
        self.sendDetails(ip, tid, deoj, seoj, esv, opc, rep_details)
        return success


    def replySetDetail_sub(self, eoj, epc):
        """!
        @brief EOJとEPCを指定した時、そのプロパティがあるかチェックする内部関数
        @param ip (str)
        @param eoj list[int]
        @param epc int
        @return そのプロパティのPDCEDT、存在しなければNone
        """
        if( eoj==EchonetLite.EOJ_NodeProfile ):
            return self.devices['0ef001'][epc]
        else:
            for i in range(0, self.instanceNumber):
                if eoj==self.eojs[i]:
                    return self.devices[self.getHexString(eoj)][epc]
            return None


    def replyInfreqDetail(self, ip, tid, seoj, deoj, esv, opc, details):
        """!
        @brief Inf_Reqに対して複数OPCに対応して返答する内部関数
        @param ip (str)
        @param tid list[int]
        @param seoj list[int]
        @param deoj list[int]
        @param esv int
        @param opc int
        @param details dict
        @return bool
        """
        success = True
        rep_details = {}  # 返信用のEPC,PDC,EDT[PDC]をすべて並べる

        for epc in details:
            devProp = self.replyInfreqDetail_sub(deoj, epc)
            if devProp == None:
                rep_details[epc] = PDCEDT([0]) # GetのエラーはPDC=0
                success = False
            else:
                rep_details[epc] = devProp

        # 返信はSEOJとDEOJが入れ替わる
        if success == True:
            # 成功したらマルチキャストでINF
            esv = EchonetLite.INF
            self.sendDetails(EchonetLite.MULTICAST_GROUP, tid, deoj, seoj, esv, opc, rep_details)
        else:
            # 失敗したらユニキャストでINF_SNA
            esv = EchonetLite.INF_SNA
            self.sendDetails(ip, tid, deoj, seoj, esv, opc, rep_details)

        return success


    def replyInfreqDetail_sub(self, eoj, epc):
        """!
        @brief EOJとEPCを指定した時、そのプロパティがあるかチェックする内部関数
        @param ip (str)
        @param seoj list[int]
        @param epc int
        @return そのプロパティのPDCEDT、存在しなければNone
        """
        if( eoj==EchonetLite.EOJ_NodeProfile ):
            return self.devices['0ef001'][epc]
        else:
            for i in range(0, self.instanceNumber):
                if eoj==self.eojs[i]:
                    return self.devices[self.getHexString(eoj)][epc]
            return None



    def replySetgetDetail(self, ip, tid, seoj, deoj, esv, opc, details):
        """!
        @brief SETGETに対して複数OPCに対応して返答する内部関数
        @param ip (str)
        @param tid list[int]
        @param seoj list[int]
        @param deoj list[int]
        @param esv int
        @param opc int
        @param details dict
        @return bool
        """
        success = True
        rep_details = {}  # 返信用のEPC,PDC,EDT[PDC]をすべて並べる

        for epc in details:
            devProp = self.replyInfreqDetail_sub(deoj, epc)
            if devProp == None:
                rep_details[epc] = PDCEDT([0]) # GetのエラーはPDC=0
                success = False
            else:
                rep_details[epc]=devProp

        # SEOJとDEOJが入れ替わる
        if success == True:
            # 成功したらマルチキャストでINF
            esv = EchonetLite.INF
            self.sendDetails(EchonetLite.MULTICAST_GROUP, tid, deoj, seoj, esv, opc, rep_details)
        else:
            # 失敗したらユニキャストでINF_SNA
            esv = EchonetLite.INF_SNA
            self.sendDetails(ip, tid, deoj, seoj, esv, opc, rep_details)
        return success


    def replyInfcDetail(self, ip, tid, seoj, deoj, esv, opc, details):
        """!
        @brief INFCに対して複数OPCに対応して返答する内部関数
        @param ip (str)
        @param tid list[int]
        @param seoj list[int]
        @param deoj list[int]
        @param esv int
        @param opc int
        @param details dict
        @return bool
        """
        success = True
        rep_details = {}  # 返信用のEPC,PDC,EDT[PDC]をすべて並べる

        for epc in details:
            devProp = self.replyInfreqDetail_sub(deoj, epc)
            if devProp == None:
                rep_details[epc] = PDCEDT([0]) # GetのエラーはPDC=0
                success = False
            else:
                rep_details[epc] = devProp

        # 返信はSEOJとDEOJが入れ替わる
        if success == True:
            # 成功したらマルチキャストでINF
            esv = EchonetLite.INFC_RES
            self.sendDetails(ip, tid, deoj, seoj, esv, opc, rep_details)
        else:
            # 失敗したらユニキャストでINF_SNA
            esv = EchonetLite.INF_SNA
            self.sendDetails(ip, tid, deoj, seoj, esv, opc, rep_details)
        return success


    def returner(self, ip:str, data):
        """!
        @brief 受信データは内部で解析して、ライブラリユーザにコールバックする
        @param ip str
        @param data list[int]
        @return boolean  True=成功, False=失敗
        """
        if self.verifyPacket(data) == False: # これ以降の解析をする価値があるか？
            return # 解析する価値なし、Drop

        # 受信データをまずは意味づけしておく
        tid = data[EchonetLite.TID:EchonetLite.SEOJ]
        seoj = data[EchonetLite.SEOJ:EchonetLite.DEOJ]
        deoj = data[EchonetLite.DEOJ:EchonetLite.ESV]
        esv = data[EchonetLite.ESV]
        opc = data[EchonetLite.OPC]
        details = self.parseDetails( esv, opc, data[EchonetLite.EPC:])

        # インスタンス0対応
        instance_min = deoj[2]
        instance_max = deoj[2] + 1

        if deoj[2] == 0:
            instance_min = 1
            instance_max = self.instanceNumber

        for i in range(instance_min, instance_max):
            deoj[2] = i

            # デバイスオブジェクトあるか
            if self.devices[ self.getHexString( deoj )] == None:
                # ないのでDrop
                continue

            # あればユーザ関数呼ぶ
            # SetはreplySetDetailの中で個別対応している
            if self.userGetFunc != None:
                for epc in details['GET']:
                    self.userGetFunc(ip, tid, seoj, deoj, esv, opc, epc, details['GET'][epc] )
            if self.userInfFunc != None:
                for epc in details['INF']:
                    self.userInfFunc(ip, tid, seoj, deoj, esv, opc, epc, details['INF'][epc] )

            if esv == EchonetLite.SETI:
                #print('### SETI ###')
                self.replySetDetail(ip, tid, seoj, deoj, esv, opc, details['SET'])
            elif esv == EchonetLite.SETC:
                #print('### SETC ###')
                self.replySetDetail(ip, tid, seoj, deoj, esv, opc, details['SET'])
            elif esv == EchonetLite.GET:
                #print('### GETI ###')
                self.replyGetDetail(ip, tid, seoj, deoj, esv, opc, details['GET'])
            elif esv == EchonetLite.INF_REQ:
                #print('### INF_REQ ###')
                self.replyInfreqDetail(ip, tid, seoj, deoj, esv, opc, details['GET'])
            elif esv == EchonetLite.SETGET:
                #print('### SETGET ###')
                self.replySetgetDetail(ip, tid, seoj, deoj, esv, opc, details)
            elif esv == EchonetLite.INFC:
                #print('### INFC ###')
                self.replyInfcDetail(ip, tid, seoj, deoj, esv, opc, details['GET'])
            #else:
                # print('### Other ###')


    def parseDetails(self, esv, opc, details):
        """!
        @brief opcを見ながらepc, pdc, edt部分を解釈
        @param esv (int)
        @param opc (int)
        @param details (list[byte])  EPC以下
        @return list(pdcedt)
        """
        sres = {} # set details
        gres = {} # get details
        ires = {} # inf details

        if( esv == EchonetLite.GET or
           esv == EchonetLite.INF_REQ or
           esv == EchonetLite.INFC ):
            i = 0
            for _ in range(0,opc):
                epc = details[i]
                pdc = details[i+1]
                gres[epc] = PDCEDT(details[i+1:i+pdc+2])
                i += pdc+2
        elif( esv == EchonetLite.SETI or
           esv == EchonetLite.SETC or
           esv == EchonetLite.SETC ):
            i = 0
            for _ in range(0,opc):
                epc = details[i]
                pdc = details[i+1]
                sres[epc] = PDCEDT(details[i+1:i+pdc+2])
                i += pdc+2
        elif( esv == EchonetLite.SETGET ): # OPC計算おかしい
            i = 0
            for _ in range(0,opc):
                epc = details[i]
                pdc = details[i+1]
                sres[epc] = PDCEDT(details[i+1:i+pdc+2])
                i += pdc+2
            for _ in range(0,opc):
                epc = details[i]
                pdc = details[i+1]
                gres[epc] = PDCEDT(details[i+1:i+pdc+2])
                i += pdc+2
        elif(  esv == EchonetLite.SETGET_RES or
                esv == EchonetLite.SETGET_SNA):
            i = 0
            for _ in range(0,opc):
                epc = details[i]
                pdc = details[i+1]
                ires[epc] = PDCEDT(details[i+1:i+pdc+2])
                i += pdc+2
            for _ in range(0,opc):
                epc = details[i]
                pdc = details[i+1]
                ires[epc] = PDCEDT(details[i+1:i+pdc+2])
                i += pdc+2
        else: # *_SNA, *_RES, INF,
            i = 0
            for _ in range(0,opc):
                epc = details[i]
                pdc = details[i+1]
                ires[epc] = PDCEDT(details[i+1:i+pdc+2])
                i += pdc+2
        return {'SET': sres, 'GET':gres, 'INF':ires}



    def parsePropertyMap(self, pdcedt):
        """!
        @brief EPC 0x9d, 0x9e, 0x9fのプロパティマップに関してedt部分を解釈
        @param pdcedt PDCEDT
        @return List[int]
        """
        #pdcedt.println()
        edt = pdcedt.edt
        profNum = edt[0]
        profs = []

        if profNum < 16:
            # format 1ならそのままの形式、ただし 個数+epc Listは pdcedt[1] に相当する
            profs = edt[1:]
        else:
            # format 2
            for bit in range(0, 8):
                for i in range(1, 17):
                    # print('bit', bit, 'i', i, 'edt', edt[i])
                    exist = ((edt[i] >> bit) & 0x01) == 1
                    if exist:
                        # 上位 (bit + 7) << 4
                        # 下位 i-1
                        epc = ((bit + 8) << 4) + (i - 1)
                        profs.append( epc )

        return profs


    def hasEOJs(self, eoj):
        """!
        @brief 指定のEOJがあるかチェック
        @param eoj List[int]
        @return bool
        @note インスタンス0は一つでもあればTrue
        """
        if (eoj == [0x0e,0xf0,0x00] or
            eoj == [0x0e,0xf0,0x01] or
            eoj == [0x0e,0xf0,0x02]):
            return True

        for v in self.eojs:
            # print(eoj, v)
            if eoj[2] == 0:
                if v[0:2] == eoj[0:2]:
                    # print("True")
                    return True
            else:
                if v == eoj:
                    # print("True")
                    return True
        return False

    def checkInfAndSend(self, obj, epc):
        """!
        @brief INFプロパティならマルチキャストで送信
        @param obj List[int]|str
        @param epc int
        """
        if type(obj) == list:
            obj = self.getHexString(obj)

        if self.devices[obj].hasInfProperty(epc):
            self.sendMultiOPC1(obj,EchonetLite.EOJ_Controller,EchonetLite.INF,epc,self.devices[obj][epc])


    def verifyPacket(self, data):
        """!
        @brief 受信パケットの正常性チェック
        @param data (list)
        @return bool
        """
        packetSize = len(data)
        #  パケットサイズが最小サイズを満たさないならDrop
        if packetSize < EchonetLite.MINIMUM_FRAME:
            return False

        # EHDがおかしいならDrop
        if data[EchonetLite.EHD1:EchonetLite.TID] != [0x10, 0x81]:
            return False

        # EOJ もってなければDrop
        deoj = data[EchonetLite.DEOJ:EchonetLite.ESV]
        if self.hasEOJs(deoj) == False:
            return False

        esv = data[EchonetLite.ESV]
        opc = data[EchonetLite.OPC]
        o = 0 # now opc
        i = EchonetLite.PDC # data へのindex 、PDC から開始

        if (esv == EchonetLite.SETI_SNA or
            esv == EchonetLite.SETC_SNA or
            esv == EchonetLite.GET_SNA or
            esv == EchonetLite.INF_SNA or
            esv == EchonetLite.SETI or
            esv == EchonetLite.SETC or
            esv == EchonetLite.GET or
            esv == EchonetLite.INF_REQ or
            esv == EchonetLite.SET_RES or
            esv == EchonetLite.GET_RES or
            esv == EchonetLite.INF or
            esv == EchonetLite.INFC or
            esv ==  EchonetLite.INFC_RES ):
            # ここから慎重にメモリアクセス
            # OPC
            while o < opc:
                if i > packetSize: # サイズ超えた
                    return False # 異常パケット
                i += 2 + data[i] # 2 byte 固定(EPC,PDC) + edtでindex更新
                o += 1
        elif ( esv == EchonetLite.SETGET or
            esv == EchonetLite.SETGET_SNA or
            esv == EchonetLite.SETGET_RES ):
            print('SETGET系は未実装です')
            return True
        else:
            return False

        return True

    def println(self):
        """!
        @brief オブジェクトの状態を表示する。主にデバッグ用
        """
        print('===== Node profile object: 0ef001')
        self.devices['0ef001'].println()
        for d in self.devices:
            if d != '0ef001':
                print('---------- Device object:', d)
                self.devices[d].println()


    def tidAutoIncrement(self):
        """!
        @brief 内部のTIDを1進める
        @note getTidString() の前に利用することを想定
        """
        if self.tid[0] == 0xff and self.tid[1] == 0xff:
            self.tid[0] = 0
            self.tid[1] = 0
        elif self.tid[1] == 0xff:
            self.tid[0] += 1
            self.tid[1] = 0
        else:
            self.tid[1] += 1

    def getTidString(self):
        """!
        @brief TIDを文字列 '0000' の形で作る
        @return str
        @note getTidString() の後に利用することを想定
        """
        return format(self.tid[0],'02x') + format(self.tid[1],'02x')

    def getHexString(self, value):
        """!
        @brief intまたはint[]を入力するとstrを出力する
        @param value (int | list[int])
        @return str
        """
        if type(value) == list:
            hexArr = [format(i,'02x') for i in value]
            return "".join(hexArr).lower()
        else:
            return format(value,'02x')

    def getInstanceList(self, value):
        """!
        @brief インスタンスリストを作る内部関数
        @param value (list[list[int]])
        @return list[int]
        """
        num = len(value)
        flat = sum(value, [])  # flatten
        flat.insert(0, num)
        return flat

    def getClassList(self, value):
        """!
        @brief クラスリストを作る内部関数
        @param value (list[list[int]])
        @return list[int]
        """
        classList = [obj[0:2] for obj in value]
        uClassList = []
        # classListにあり、uClassListにないものを探してリストアップする
        for v in classList:
            exist = False
            for w in uClassList:
                if v==w:
                    exist = True
            if exist == False:
                uClassList.append(v)
        num = len(uClassList)
        flat = sum(uClassList, [])
        flat.insert(0, num)
        return flat

    def getHwAddr(self):
        """!
        @brief Macアドレスを list[6] の型で求める
        @return list[int] size 6
        """
        if platform.system() == 'Windows': # windows
            mac = uuid.getnode()
            macStr = ':'.join(re.findall('..', '%012x' % mac))
            ar = macStr.split(':')[0:6]
            return [int(x,16) for x in ar]
        elif platform.system() == 'Darwin': # Mac
            mac = uuid.getnode()
            macStr = ':'.join(re.findall('..', '%012x' % mac))
            ar = macStr.split(':')[0:6]
            return [int(x,16) for x in ar]
        else:
            return [0,0,0,0,0,0]



if __name__ == '__main__':
    print("===== echonet_lite.py unit test")
    el = EchonetLite( [EchonetLite.EOJ_Controller] )
    el.println()
    print("- parseDetails()")
    #print( el.parseDetails(1, [0x80, 0x00]))
    #print( el.parseDetails(1, [0x80, 0x01, 0x30]) )
    #print( el.parseDetails(2, [0x80, 0x01, 0x30, 0x81, 0x02, 0x31, 0x32]) )
    #el.parseDetails(2, [0x80, 0x00, 0x81, 0x00])
    print("- getHexString()")
    #print(el.getHexString([1,2,3,4]))
    print("- replyGetDetail_sub()")
    print( el.replyGetDetail_sub( EchonetLite.EOJ_Controller, 0x84) )
    t = PDCEDT()
    t.setEDT([0x02, 0x81, 0x82])
    print( el.parsePropertyMap(t) )
    t.setEDT([0x10, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01])
    print( el.parsePropertyMap(t) )
    el.sendOPC1( '192.168.86.158', '05ff01', '0ef001', '62', '80', '00')
