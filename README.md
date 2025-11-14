# ELPython

ECHONET Lite protocol implementation for Python

[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-181%20passed-brightgreen.svg)](v0/test_EchonetLite_for3.10)

## 📖 概要

ELPythonは、日本のスマートホーム規格である**ECHONET Lite**プロトコルをPythonで実装したライブラリです。家電機器やセンサーとの通信を簡単に行えます。

### 特徴

- ✨ **シンプルなAPI** - 直感的で使いやすいインターフェース
- 🔒 **堅牢なバリデーション** - 入力値の厳密なチェック
- 🧪 **高いテストカバレッジ** - 181個のユニットテスト (71%カバレッジ)
- 🌍 **クロスプラットフォーム** - Windows/macOS/Linux対応
- 📦 **依存関係なし** - 標準ライブラリのみで動作
- 🚀 **高速** - 効率的な実装

## 🎯 対応バージョン

- **Python 3.10以降** (for3.10ディレクトリ)
- **Python 3.4/MicroPython** (for3.4ディレクトリ)

## 📦 インストール

### 標準的なインストール

```bash
# リポジトリをクローン
git clone https://github.com/Hiroshi-Sugimura/ELPython.git
cd ELPython

# Python 3.10以降の場合
cd v0/EchonetLite_for3.10
```

### 依存関係

**なし!** 標準ライブラリのみで動作します 🎉

## 🚀 クイックスタート

### 基本的な使い方

```python
from EchonetLite import EchonetLite, PDCEDT

# コントローラーとして初期化
el = EchonetLite()

# コールバック関数を定義
def on_set(ip, tid, seoj, deoj, esv, opc, epc, pdcedt):
    print(f"SET受信: {ip} EPC={hex(epc)}")
    return True

def on_get(ip, tid, seoj, deoj, esv, opc, epc, pdcedt):
    print(f"GET受信: {ip} EPC={hex(epc)}")
    return True

def on_inf(ip, tid, seoj, deoj, esv, opc, epc, pdcedt):
    print(f"INF受信: {ip} EPC={hex(epc)}")
    return True

# 受信開始
el.begin(on_set, on_get, on_inf)

# 機器検索
el.sendMultiOPC1(
    el.EOJ_Controller,
    '0ef001',  # ノードプロファイル
    '62',      # GET
    'd6',      # インスタンスリスト通知
    '00'       # PDC+EDT
)
```

### デバイスのプロパティ更新

```python
# コントローラーのプロパティを更新
el.update('05ff01', 0x80, [0x30])  # 動作状態をONに

# カスタムデバイスの追加
el.update([0x02, 0x90, 0x01], 0x80, [0x30])  # 一般照明
```

### データの取得

```python
# 16進数文字列に変換
hex_str = el.getHexString([0x10, 0x81])  # "1081"

# TIDの取得
tid = el.getTidString()  # 自動インクリメントされるTID
```

## 🧪 テストの実行

### 環境構築

```bash
cd v0/test_EchonetLite_for3.10

# 仮想環境の作成
python3 -m venv venv

# 仮想環境の有効化 (macOS/Linux)
source venv/bin/activate

# 仮想環境の有効化 (Windows)
venv\Scripts\activate

# 依存パッケージのインストール
pip install pytest pytest-cov pytest-mock
```

### テスト実行コマンド

```bash
# 全テストの実行
pytest

# 詳細表示
pytest -v

# カバレッジ付き実行
pytest --cov --cov-report=html

# 特定のテストファイルのみ
pytest test_echonet_lite.py -v

# 特定のテストクラスのみ
pytest test_echonet_lite.py::TestEchonetLiteInit -v
```

### 便利なシェルスクリプト

```bash
# setup.sh - 初回セットアップ
./setup.sh

# run_tests.sh - テスト実行
./run_tests.sh              # 通常実行
./run_tests.sh -v           # 詳細表示
./run_tests.sh --cov        # カバレッジ計測
```

## 📁 プロジェクト構成

```
ELPython/
├── README.md
├── LICENSE
└── v0/
    ├── EchonetLite_for3.10/          # Python 3.10以降用
    │   ├── __init__.py
    │   ├── EchonetLite.py            # メインクラス
    │   ├── ELOBJ.py                  # オブジェクト管理
    │   ├── PDCEDT.py                 # プロパティデータ管理
    │   └── utils.py                  # ユーティリティ関数
    ├── test_EchonetLite_for3.10/     # ユニットテスト
    │   ├── conftest.py
    │   ├── test_echonet_lite.py      # 54テスト
    │   ├── test_elobj.py             # 57テスト
    │   ├── test_pdcedt.py            # 41テスト
    │   ├── test_utils.py             # 24テスト
    │   ├── test_echonet_lite_protocol.py # 22テスト (プロトコル準拠)
    │   ├── setup.sh                  # セットアップスクリプト
    │   └── run_tests.sh              # テスト実行スクリプト
    ├── sample_Controller_f3.10/      # コントローラーサンプル
    ├── sample_GeneralLighting_f3.10/ # 照明デバイスサンプル
    └── sample_SSNG/                  # SSNGサンプル
```

## 📚 API リファレンス

### EchonetLiteクラス

#### 初期化

```python
el = EchonetLite(eojs=None, options=None)
```

- `eojs`: EOJ（ECHONET Liteオブジェクト）のリスト (デフォルト: コントローラー)
- `options`: オプション辞書 (`{"debug": True}` でデバッグモード)

#### 主要メソッド

| メソッド | 説明 |
|---------|------|
| `begin(sfunc, gfunc, ifunc)` | 受信開始。コールバック関数を設定 |
| `update(eoj, epc, edt)` | デバイスプロパティの更新 |
| `sendMultiOPC1(seoj, deoj, esv, epc, pdcedt)` | マルチキャスト送信 (1プロパティ) |
| `sendOPC1(ip, seoj, deoj, esv, epc, pdcedt)` | ユニキャスト送信 (1プロパティ) |
| `getHexString(data)` | バイト列を16進数文字列に変換 |
| `getTidString()` | トランザクションIDを取得 |
| `parsePropertyMap(pdcedt)` | プロパティマップを解析 |

### 定数

```python
# ESV (ECHONET Lite Service)
EchonetLite.SETI      # 0x60 - プロパティ値書き込み要求（応答不要）
EchonetLite.SETC      # 0x61 - プロパティ値書き込み要求（応答要）
EchonetLite.GET       # 0x62 - プロパティ値読み出し要求
EchonetLite.INF       # 0x73 - プロパティ値通知
EchonetLite.SETGET    # 0x6E - プロパティ値書き込み・読み出し要求

# EOJ (ECHONET Lite Object)
EchonetLite.EOJ_Controller     # [0x05, 0xff, 0x01] - コントローラー
EchonetLite.EOJ_NodeProfile    # [0x0e, 0xf0, 0x01] - ノードプロファイル
```

## 🔧 開発

### バリデーション機能

全ての入力パラメータに厳密なバリデーションが実装されています:

```python
# 型チェック
el.update([0x05, 0xff, 0x01], 0x80, [0x30])  # ✅ OK
el.update("invalid", 0x80, [0x30])           # ❌ TypeError

# 値範囲チェック
el.update([0x05, 0xff, 0x01], 0x80, [256])   # ❌ ValueError
el.update([0x05, 0xff, 0x01], -1, [0x30])    # ❌ ValueError
```

### デバッグモード

```python
el = EchonetLite(options={"debug": True})
# デバッグメッセージが出力されます
```

## 📊 テストカバレッジ

- **総テスト数**: 198個
- **成功**: 181個
- **スキップ**: 17個 (将来実装予定のプロトコル機能)
- **カバレッジ**: 71%

### テスト内訳

| テストファイル | テスト数 | カバー内容 |
|---------------|---------|----------|
| test_echonet_lite.py | 54 | メインクラスの機能 |
| test_elobj.py | 57 | オブジェクト管理 |
| test_pdcedt.py | 41 | プロパティデータ |
| test_utils.py | 24 | ユーティリティ関数 |
| test_echonet_lite_protocol.py | 22 | プロトコル準拠性 |

## 🤝 コントリビューション

Issue、Pull Requestお待ちしています!

### 開発手順

1. このリポジトリをフォーク
2. フィーチャーブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. Pull Requestを作成

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細は[LICENSE](LICENSE)ファイルをご覧ください。

## 👤 作者

**Hiroshi Sugimura**
- GitHub: [@Hiroshi-Sugimura](https://github.com/Hiroshi-Sugimura)
- 所属: Kanagawa Institute of Technology

## 🙏 謝辞

- ECHONET Lite規格: [ECHONET Consortium](https://echonet.jp/)
- テストフレームワーク: [pytest](https://pytest.org/)

## 📝 変更履歴

### v0 (unitTestブランチ)
- ✨ 包括的なユニットテスト追加 (198テスト)
- 🔒 全APIに厳密なバリデーション実装
- 🌍 クロスプラットフォーム対応強化
- 📦 外部依存関係の削除 (ipget → 標準ライブラリ)
- 🛠️ utils.pyの追加 (共通ユーティリティ)
- 🐛 デストラクタのバグ修正
- 📚 プロトコル準拠テストの追加

---

**ECHONET Liteで、あなたのスマートホームをもっと便利に! 🏠✨**
