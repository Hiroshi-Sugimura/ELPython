#!/usr/bin/python3
# -*- coding: utf8 -*-

import platform
import socket
if platform.system() == 'Linux':
    import ipget  #  インストール必要, for Linux
import tkinter as tk
import threading
import time
import datetime
import json
from EchonetLite import EchonetLite, PDCEDT


#====================================================================================================
# EchonetLite, list表示する内部データ
facilities:dict[str, dict[str, dict[str, str]]] = {} # ECHONET Liteネットワーク機器

#====================================================================================================
# Windowを定義
class MainWin:
    selected_ip = ''
    selected_eoj = ''
    selected_epc = ''
    ips = []
    eojs = []
    epcs = []
    edts = []
    window = None

    #  コンストラクタ
    def __init__(self):
        # main window
        ## rootウィンドウを作成
        self.window = tk.Tk()
        ## Window作る
        self.createWindow(self.window)

    def mainloop(self):
        self.window.mainloop()

    # GUI作成
    def createWindow(self, win_main):
        # rootウィンドウのタイトルを変える
        win_main.title("SSNGpy")

        win_main.geometry("1024x768")    # rootウィンドウの大きさを1024x768に
        win_main.minsize(1024,768)

        # facilities表示データ
        lb_ips_items = tk.StringVar(value=self.ips)
        lb_eojs_items = tk.StringVar(value=self.eojs)
        lb_epcs_items = tk.StringVar(value=self.epcs)
        lb_edts_items = tk.StringVar(value=self.edts)

        # フレーム
        frm_ip_btn = tk.Frame(win_main)
        frm_control = tk.Frame(win_main)
        frm_facilities = tk.Frame(win_main)
        frm_log = tk.Frame(win_main)

        # Label部品を作る
        lbl_myip = tk.Label(frm_ip_btn, text="My IP:")
        self.lbl_srcip_text = tk.StringVar(frm_ip_btn)
        self.lbl_srcip_text.set('192.168.x.y')
        lbl_srcip = tk.Label(frm_ip_btn, textvariable=self.lbl_srcip_text, font='Courier 12')
        lbl_dstip = tk.Label(frm_ip_btn, text="DST IP:")

        lbl_deoj = tk.Label(frm_control, text="DEOJ:")
        lbl_esv = tk.Label(frm_control, text="ESV:")
        lbl_epc = tk.Label(frm_control, text="EPC:")
        lbl_edt = tk.Label(frm_control, text="EDT:")

        lbl_ips = tk.Label(frm_facilities, text="IP")
        lbl_eojs = tk.Label(frm_facilities, text="EOJ")
        lbl_epcs = tk.Label(frm_facilities, text="EPC")
        lbl_edts = tk.Label(frm_facilities, text="PDC, EDT")

        # 入力ボックス ip
        tx_dstip = tk.Entry(frm_ip_btn, font='Courier 12')
        tx_dstip.insert(0, '224.0.23.0')

        # 入力ボックス control
        tx_deoj = tk.Entry(frm_control, font='Courier 12')
        tx_deoj.insert(0, '029001')
        tx_esv = tk.Entry(frm_control, font='Courier 12')
        tx_esv.insert(0, '62')
        tx_epc = tk.Entry(frm_control, font='Courier 12')
        tx_epc.insert(0, '80')
        tx_edt = tk.Entry(frm_control, font='Courier 12')
        tx_edt.insert(0, '30')

        # ボタンを作る
        def btn_search_clicked():
            el.sendMultiOPC1( el.EOJ_Controller, '0ef001', '62', 'd6', '00') # search
        btn_search = tk.Button(frm_ip_btn, text="Search", command= lambda : btn_search_clicked())

        def btn_send_clicked():
            if tx_dstip.get() == '224.0.23.0':
                pdcedt = el.getHexString( len(tx_edt.get())//2 )+ tx_edt.get()
                el.sendMultiOPC1( el.EOJ_Controller, tx_deoj.get(), tx_esv.get(), tx_epc.get(), pdcedt) # send
            else:
                pdcedt = el.getHexString( len(tx_edt.get())//2 )+ tx_edt.get()
                el.sendOPC1( tx_dstip.get(), el.EOJ_Controller, tx_deoj.get(), tx_esv.get(), tx_epc.get(), pdcedt) # send
        btn_send  = tk.Button(frm_ip_btn, text="Send", command= lambda : btn_send_clicked())

        def btn_update_clicked():
            self.ips = []
            for key in facilities:
                self.ips.append(key)
            lb_ips_items.set(self.ips)
        btn_update = tk.Button(frm_facilities, text="Update", command= lambda : btn_update_clicked())

        # Listbox, ipをクリックした
        def lb_ips_selected(event):
            selected_index = lb_ips.curselection()
            if selected_index:
                self.selected_ip = lb_ips.get(selected_index)
                self.eojs = []
                for key in facilities[self.selected_ip]:
                    self.eojs.append(key)
                lb_eojs_items.set(self.eojs)

        # Listbox, eojsをクリックした
        def lb_eojs_selected(event):
            selected_eojs_index = lb_eojs.curselection()
            if selected_eojs_index:
                self.selected_eoj = lb_eojs.get(selected_eojs_index)
                self.epcs = []
                for key in facilities[self.selected_ip][self.selected_eoj]:
                    self.epcs.append(key)
                lb_epcs_items.set(self.epcs)

        # Listbox, epcsをクリックした
        def lb_epcs_selected(event):
            selected_epcs_index = lb_epcs.curselection()
            if selected_epcs_index:
                self.selected_epc = lb_epcs.get(selected_epcs_index)
                self.edts = []
                for key in facilities[self.selected_ip][self.selected_eoj][self.selected_epc]:
                    self.edts.append(key + ' : ' + facilities[self.selected_ip][self.selected_eoj][self.selected_epc][key])
                lb_edts_items.set(self.edts)

        # テキストエリア
        lbl_log = tk.Label(frm_log, text="Log")
        self.ta_log = tk.Text(frm_log)
        self.ta_log.configure(font='Courier 12')
        # scroll
        sc_ta_log = tk.Scrollbar(frm_log,orient='vertical',command=self.ta_log.yview)
        self.ta_log['yscrollcommand'] = sc_ta_log.set
        self.ta_log.insert(1.0, '==== Received ====')

        # IPリスト
        lb_ips = tk.Listbox(frm_facilities, selectmode="single", font='Courier 12', listvariable=lb_ips_items)
        sc_lb_ips = tk.Scrollbar(frm_facilities,orient='vertical',command=lb_ips.yview)
        lb_ips['yscrollcommand'] = sc_lb_ips.set
        lb_ips.bind('<<ListboxSelect>>', lb_ips_selected)

        # EOJリスト
        lb_eojs = tk.Listbox(frm_facilities, selectmode="single", font='Courier 12', listvariable=lb_eojs_items)
        sc_lb_eojs = tk.Scrollbar(frm_facilities,orient='vertical',command=lb_eojs.yview)
        lb_eojs['yscrollcommand'] = sc_lb_eojs.set
        lb_eojs.bind('<<ListboxSelect>>', lb_eojs_selected)

        # EPCリスト
        lb_epcs = tk.Listbox(frm_facilities, selectmode="single", font='Courier 12', listvariable=lb_epcs_items)
        sc_lb_epcs = tk.Scrollbar(frm_facilities,orient='vertical',command=lb_epcs.yview)
        lb_epcs['yscrollcommand'] = sc_lb_epcs.set
        lb_epcs.bind('<<ListboxSelect>>', lb_epcs_selected)

        # EDTリスト
        lb_edts = tk.Listbox(frm_facilities, selectmode="single", font='Courier 12', listvariable=lb_edts_items)
        sc_lb_edts = tk.Scrollbar(frm_facilities,orient='vertical',command=lb_edts.yview)
        lb_edts['yscrollcommand'] = sc_lb_edts.set

        # 表示 frm_ip_btn
        lbl_myip.pack(side = tk.LEFT)
        lbl_srcip.pack(side = tk.LEFT)
        lbl_dstip.pack(side = tk.LEFT)
        tx_dstip.pack(side = tk.LEFT)
        btn_send.pack(side = tk.LEFT)
        btn_search.pack(side = tk.LEFT)

        # 表示 frm_control
        lbl_deoj.pack(side = tk.LEFT)
        tx_deoj.pack(side = tk.LEFT)
        lbl_esv.pack(side = tk.LEFT)
        tx_esv.pack(side = tk.LEFT)
        lbl_epc.pack(side = tk.LEFT)
        tx_epc.pack(side = tk.LEFT)
        lbl_edt.pack(side = tk.LEFT)
        tx_edt.pack(side = tk.LEFT)

        # 表示 frm_facilities
        lbl_ips.grid(row=0,column=0)
        lbl_eojs.grid(row=0,column=2)
        lbl_epcs.grid(row=0,column=4)
        lbl_edts.grid(row=0,column=6)
        btn_update.grid(row=0,column=8)
        lb_ips.grid(row=1,column=0, sticky=tk.NS)
        sc_lb_ips.grid(row=1,column=1, sticky=tk.NS)
        lb_eojs.grid(row=1,column=2, sticky=tk.NS)
        sc_lb_eojs.grid(row=1,column=3, sticky=tk.NS)
        lb_epcs.grid(row=1,column=4, sticky=tk.NS)
        sc_lb_epcs.grid(row=1,column=5, sticky=tk.NS)
        lb_edts.grid(row=1,column=6, sticky=tk.NSEW)
        sc_lb_edts.grid(row=1,column=7, sticky=tk.NS)
        frm_facilities.rowconfigure(1, weight=1)
        frm_facilities.columnconfigure(6, weight=1)

        # 表示 frm_log
        lbl_log.grid(row=0, column=0)
        self.ta_log.grid(row=1, column=0, sticky=tk.NSEW)
        sc_ta_log.grid(row=1, column=1, sticky=tk.NS)
        frm_log.rowconfigure(1, weight=1)
        frm_log.columnconfigure(0, weight=1)

        # 全体表示
        frm_ip_btn.pack(anchor=tk.W)
        frm_control.pack(anchor=tk.W)
        frm_facilities.pack(expand=True, anchor=tk.W, fill=tk.BOTH)
        frm_log.pack(expand=True, anchor=tk.W, fill=tk.BOTH)


# window 作っておく（win がglobalとしてアクセスできるように）
win = MainWin()


#====================================================================================================
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
    global win
    #print("---------- Set")
    #print("from:", ip)
    #print("TID:", el.getHexString(tid), "SEOJ:", el.getHexString(seoj), "DEOJ:", el.getHexString(deoj), "ESV:", el.getHexString(esv), "OPC:", el.getHexString(opc), "EPC:", el.getHexString(epc), pdcedt.printString())
    msg = ip + ' ' + el.getHexString(tid) + ' ' + el.getHexString(seoj) + ' ' + el.getHexString(deoj) + ' ' + el.getHexString(esv) + ' ' + el.getHexString(opc) + ' ' + el.getHexString(epc) + ' ' + el.getHexString(pdcedt.pdc) + ' ' + el.getHexString(pdcedt.edt)

    win.ta_log.insert('1.0', msg + '\n')

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
    global win
    #print("---------- Get")
    #print("from:", ip)
    #print("TID:", el.getHexString(tid), "SEOJ:", el.getHexString(seoj), "DEOJ:", el.getHexString(deoj), "ESV:", el.getHexString(esv), "OPC:", el.getHexString(opc), "EPC:", el.getHexString(epc), pdcedt.printString())
    msg = ip + ' ' + el.getHexString(tid) + ' ' + el.getHexString(seoj) + ' ' + el.getHexString(deoj) + ' ' + el.getHexString(esv) + ' ' + el.getHexString(opc) + ' ' + el.getHexString(epc) + ' ' + el.getHexString(pdcedt.pdc) + ' ' + el.getHexString(pdcedt.edt)

    win.ta_log.insert('1.0', msg + '\n')

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
    global win
    #print("---------- INF, RES, SNA")
    #print("from:", ip)
    #print("TID:", el.getHexString(tid), "SEOJ:", el.getHexString(seoj), "DEOJ:", el.getHexString(deoj), "ESV:", el.getHexString(esv), "OPC:", el.getHexString(opc), "EPC:", el.getHexString(epc), pdcedt.printString())
    msg = ip + ' ' + el.getHexString(tid) + ' ' + el.getHexString(seoj) + ' ' + el.getHexString(deoj) + ' ' + el.getHexString(esv) + ' ' + el.getHexString(opc) + ' ' + el.getHexString(epc) + ' ' + el.getHexString(pdcedt.pdc) + ' ' + el.getHexString(pdcedt.edt)

    win.ta_log.insert('1.0', msg + '\n')

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


# 毎分、状態監視用パケットを作るスレッド
def observerThread():
    while True:
        el.sendMultiOPC1( el.EOJ_Controller, '013000', '62', '80', '00') # ホームエアコン
        el.sendMultiOPC1( el.EOJ_Controller, '013500', '62', '80', '00') # 空気清浄機
        el.sendMultiOPC1( el.EOJ_Controller, '015600', '62', '80', '00') # 業務用パッケージエアコン室内機
        el.sendMultiOPC1( el.EOJ_Controller, '015700', '62', '80', '00') # 業務用パッケージエアコン室外機
        el.sendMultiOPC1( el.EOJ_Controller, '029000', '62', '80', '00') # 一般照明
        #now = datetime.datetime.now()
        #print("Got data at", now.strftime("%Y年%m月%d日 %H時%M分%S秒")) # フォーマットして出力
        #print(getFacilitiesJson(facilities))
        time.sleep(60) # 1 min


#====================================================================================================
# 開始
# 自分のip
myip = ''
if platform.system() == 'Linux': # for Linux
    localIP = ipget.ipget()
    # print(localIP.ipaddr("wlan0"))
    myip = str(localIP.ipaddr("wlan0")).split('/')[0] # for Linux
elif platform.system() == 'Darwin': # mac
    myip = socket.gethostbyname(socket.gethostname()) # for mac
else:
    myip = socket.gethostbyname(socket.gethostname()) # for windows
win.lbl_srcip_text.set(myip)


# EL
el = EchonetLite([[0x05,0xff,0x01]]) # Controller
el.update([0x05,0xff,0x01], 0x9d, [0x80, 0xd6])
el.update([0x05,0xff,0x01], 0x9e, [0x80])
el.update([0x05,0xff,0x01], 0x9f, [0x80, 0x81, 0x82, 0x83, 0x88, 0x8a, 0x9d, 0x9e, 0x9f])
el.begin(userSetFunc, userGetFunc, userInfFunc)
el.sendMultiOPC1( el.EOJ_NodeProfile, el.EOJ_NodeProfile, el.GET, 0xd6, PDCEDT([0])) # インスタンスリスト取得
observer_thread = threading.Thread(target=observerThread) # スレッドで動かす
observer_thread.start()

# Window起動
win.mainloop()
