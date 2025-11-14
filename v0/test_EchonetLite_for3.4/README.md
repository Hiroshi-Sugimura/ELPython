# EchonetLite テスト (Python 3.4 Compatible Version)

このディレクトリには、EchonetLite_for3.4(uPy)ライブラリの単体テストが含まれています。
Python 3.4互換コードをPython 3.10環境でテストします。

## 📋 概要

- **対象ライブラリ**: `../EchonetLite_for3.4(uPy)/`
- **テスト環境**: Python 3.10.x + pytest
- **互換性**: Python 3.4.0互換コード(MicroPython対応)
- **カバレッジ目標**: 70%以上

## 🚀 クイックスタート

### 1. テスト環境のセットアップ

```bash
cd /Users/sugimura/Documents/ELPython/v0/test_EchonetLite_for3.4
chmod +x setup.sh run_tests.sh
./setup.sh
```

### 2. テストの実行

```bash
# 仮想環境を有効化
source venv/bin/activate

# 全テストを実行
pytest

# 詳細表示
pytest -v

# カバレッジ付き実行
pytest --cov

# HTMLカバレッジレポート生成
pytest --cov --cov-report=html

# 特定のテストファイルのみ実行
pytest test_pdcedt.py
pytest test_utils.py -v

# 仮想環境を無効化
deactivate
```

### 3. ワンライナーでテスト実行

```bash
./run_tests.sh
./run_tests.sh -v
./run_tests.sh --cov
```

## 📁 テストファイル構成

```
test_EchonetLite_for3.4/
├── __init__.py                          # テストパッケージ初期化
├── conftest.py                          # pytest設定とフィクスチャ
├── test_utils.py                        # utils.pyのテスト (24 tests)
├── test_pdcedt.py                       # PDCEDT.pyのテスト (41 tests)
├── test_elobj.py                        # ELOBJ.pyのテスト (57 tests)
├── test_echonet_lite.py                 # EchonetLite.pyのテスト (54 tests)
├── test_echonet_lite_protocol.py        # プロトコル準拠テスト (22 tests)
├── setup.sh                             # 環境セットアップスクリプト
├── run_tests.sh                         # テスト実行スクリプト
├── .gitignore                           # Git除外設定
└── README.md                            # このファイル
```

## 🧪 テストケース詳細

### test_utils.py (24 tests)
- `deepcopy_list()`: リストのディープコピー
- `deepcopy_dict_pdcedt()`: PDCEDT辞書のディープコピー
- エッジケース、実世界シナリオ

### test_pdcedt.py (41 tests)
- コンストラクタ(None, PDCEDT, list)
- バリデーション(型チェック、範囲チェック)
- EDT操作(setEDT, getString, printString)
- 等価比較演算子

### test_elobj.py (57 tests)
- コンストラクタとコピーコンストラクタ
- PDCEDT管理(SetPDCEDT, GetPDCEDT, SetEDT)
- PropertyMap管理(INF/SET/GET)
- 配列インターフェース(`__getitem__`, `__setitem__`)
- バリデーション(EPC範囲チェック)

### test_echonet_lite.py (54 tests)
- 初期化と設定
- ネットワーク通信(送信機能)
- プロトコル処理
- デバイス管理
- ユーティリティメソッド

### test_echonet_lite_protocol.py (22 tests)
- ECHONET Lite規格準拠テスト
- フレーム構造検証
- ESV処理
- OPC処理

## 📊 テスト実行例

```bash
$ pytest -v
========================= test session starts ==========================
platform darwin -- Python 3.10.6, pytest-9.0.1
collected 198 items

test_utils.py::TestDeepcopyList::test_deepcopy_list_normal PASSED  [  1%]
test_utils.py::TestDeepcopyList::test_deepcopy_list_empty PASSED   [  2%]
...
test_pdcedt.py::TestPDCEDT::test_init_default PASSED               [ 50%]
test_elobj.py::TestELOBJ::test_init_default PASSED                 [ 75%]
test_echonet_lite.py::TestInit::test_init_default PASSED           [ 90%]
========================= 198 passed in 2.5s ===========================
```

## 🎯 カバレッジレポート

```bash
$ pytest --cov --cov-report=term-missing
---------- coverage: platform darwin, python 3.10.6 -----------
Name                                           Stmts   Miss  Cover   Missing
----------------------------------------------------------------------------
../EchonetLite_for3.4(uPy)/ELOBJ.py              XXX    XX    XX%   xxx-xxx
../EchonetLite_for3.4(uPy)/EchonetLite.py        XXX    XX    XX%   xxx-xxx
../EchonetLite_for3.4(uPy)/PDCEDT.py             XXX    XX    XX%   xxx-xxx
../EchonetLite_for3.4(uPy)/utils.py              XXX    XX    XX%   xxx-xxx
----------------------------------------------------------------------------
TOTAL                                           XXXX   XXX    XX%
```

HTMLレポートは `htmlcov/index.html` で確認できます。

## 🔍 Python 3.4互換性について

### テストしているコード
- **ターゲット**: `EchonetLite_for3.4(uPy)/`
- **特徴**:
  - 型ヒント無し
  - f-string未使用(`.format()`使用)
  - MicroPython互換
  - 外部依存ゼロ

### テスト環境
- **実行環境**: Python 3.10 + pytest
- **理由**: Python 3.4互換コードはPython 3.10でも動作する
- **メリット**:
  - ✅ pytestの全機能が使える
  - ✅ カバレッジ測定可能
  - ✅ CI/CD統合可能
  - ✅ 高速なテスト実行

### 注意事項
⚠️ 実機特有の動作(ESP32/Raspberry Pi Pico)はテストできません
- MicroPythonのメモリ制約
- 実際のネットワーク環境
- ハードウェア依存機能

これらは別途実機テストが必要です。

## 🛠️ トラブルシューティング

### venvが作成できない
```bash
# Python 3のインストールを確認
python3 --version

# venvモジュールがない場合
# macOS/Linux
sudo apt-get install python3-venv  # Ubuntu/Debian
brew install python3  # macOS

# Windows
py -m pip install virtualenv
```

### テストが見つからない
```bash
# conftest.pyのパス設定を確認
cat conftest.py | grep echonet_dir

# 手動でパスを追加して確認
python3 -c "import sys; sys.path.insert(0, '../EchonetLite_for3.4(uPy)'); from EchonetLite import PDCEDT; print('OK')"
```

### カバレッジが取れない
```bash
# pytest-covのインストール確認
pip list | grep pytest-cov

# 再インストール
pip install --upgrade pytest-cov
```

## 📝 テスト追加ガイド

新しいテストを追加する場合:

1. 適切なテストファイルを選択/作成
2. テストクラスを作成
3. `test_`で始まるメソッドを追加
4. アサーションで検証
5. `pytest -v` で確認

```python
class TestNewFeature:
    """新機能のテスト"""

    def test_something(self):
        """テストの説明"""
        # Arrange
        expected = 42

        # Act
        actual = new_feature()

        # Assert
        assert actual == expected
```

## 🔗 関連リンク

- [pytest公式ドキュメント](https://docs.pytest.org/)
- [pytest-cov公式ドキュメント](https://pytest-cov.readthedocs.io/)
- [EchonetLite 3.10版テスト](../test_EchonetLite_for3.10/)
- [ECHONET Lite規格書](https://echonet.jp/spec_g/)

## ✨ 更新履歴

- 2025-11-14: 初版作成
  - Python 3.4版テストスイート構築
  - 198テストケース移植
  - カバレッジ測定環境構築
