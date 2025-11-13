# EchonetLite テストスイート 🧪

このディレクトリには、EchonetLite_for3.10ライブラリの単体テストが含まれています。

## 📦 セットアップ

### 自動セットアップ（推奨）

```bash
# test_EchonetLite_for3.10ディレクトリに移動
cd v0/test_EchonetLite_for3.10

# セットアップスクリプトに実行権限を付与
chmod +x setup.sh

# 実行（venvを作成して依存関係をインストール）
./setup.sh
```

このスクリプトは以下を自動で行います：
- 仮想環境(venv)の作成
- pipのアップグレード
- pytest, pytest-cov, pytest-mockのインストール

### 手動セットアップ

```bash
cd v0/test_EchonetLite_for3.10

# 仮想環境を作成
python3 -m venv venv

# 仮想環境を有効化
source venv/bin/activate

# 依存パッケージをインストール
pip install pytest pytest-cov pytest-mock
```

## 🧪 テスト実行方法

### スクリプトで実行（簡単！）

```bash
# test_EchonetLite_for3.10ディレクトリで実行
chmod +x run_tests.sh
./run_tests.sh              # デフォルト（-vオプション付き）
./run_tests.sh --cov        # カバレッジ付き
./run_tests.sh -k "init"    # 特定のテストのみ
```

### 手動で実行

まず仮想環境を有効化してから実行します：

```bash
# test_EchonetLite_for3.10ディレクトリで実行
source venv/bin/activate

# 基本的な実行
pytest

# 詳細表示
pytest -v
```

### その他の実行オプション

```bash
# 仮想環境を有効化してから実行
source venv/bin/activate

# 詳細表示
pytest -v
pytest -vv  # さらに詳細

# カバレッジ付き実行
pytest --cov

# HTMLレポート生成
pytest --cov --cov-report=html
open htmlcov/index.html  # macの場合

# 終了後は仮想環境を無効化（任意）
deactivate
```

### 特定のテストのみ実行

```bash
source venv/bin/activate

# ファイル指定
pytest test_echonet_lite.py

# クラス指定
pytest test_echonet_lite.py::TestEchonetLiteInit

# 関数指定
pytest test_echonet_lite.py::TestEchonetLiteInit::test_init_default_controller

# キーワード検索
pytest -k "init"  # "init"を含むテストのみ実行
pytest -k "not slow"  # "slow"を含まないテストを実行
```

### 失敗したテストのみ再実行
```bash
pytest --lf  # last failed
pytest --ff  # failed first (失敗を先に実行)
```

### 並列実行（高速化）
```bash
# pytest-xdistが必要: pip install pytest-xdist
pytest -n auto  # CPUコア数に応じて自動
pytest -n 4     # 4プロセスで実行
```

### デバッグモード
```bash
# 最初の失敗で停止
pytest -x

# 詳細なトレースバック
pytest --tb=long

# print文を表示
pytest -s
```

## 📁 テストの構成

```
v0/
├── pyproject.toml              # プロジェクト設定とpytest設定
├── EchonetLite_for3.10/       # ライブラリ本体
│   ├── __init__.py
│   ├── EchonetLite.py
│   ├── PDCEDT.py
│   └── ELOBJ.py
└── test_EchonetLite_for3.10/  # テストコード（このディレクトリ）
    ├── venv/                   # 仮想環境（setup.shで作成）
    ├── setup.sh                # セットアップスクリプト
    ├── run_tests.sh            # テスト実行スクリプト
    ├── README.md               # このファイル
    ├── __init__.py
    ├── conftest.py             # pytest設定とフィクスチャ
    ├── test_echonet_lite.py   # EchonetLiteクラスのテスト
    ├── test_pdcedt.py         # PDCEDTクラスのテスト（今後追加予定）
    └── test_elobj.py          # ELOBJクラスのテスト（今後追加予定）
```

## テストカバレッジ

現在のテストでカバーしている機能:

### EchonetLiteクラス
- ✅ 初期化（デフォルト、カスタムEOJ、複数EOJ）
- ✅ ユーティリティ関数（getHexString, tidAutoIncrement, getTidString）
- ✅ プロパティマップ解析（形式1、形式2）
- ✅ EOJチェック（hasEOJs）
- ✅ パケット検証（verifyPacket）
- ✅ インスタンスリスト生成（getInstanceList, getClassList）
- ✅ 定数定義（ESV、EOJ、ネットワーク定数）
- ✅ デバイス管理（初期プロパティ、更新）

### 今後追加予定
- ⏳ PDCEDTクラスのテスト
- ⏳ ELOBJクラスのテスト
- ⏳ 送受信機能の統合テスト

## カスタムマーク

```python
@pytest.mark.slow          # 時間のかかるテスト
@pytest.mark.network       # ネットワークを使うテスト
@pytest.mark.integration   # 統合テスト
```

実行時にマークでフィルタ:
```bash
pytest -m "not slow"       # slowマークのないテストのみ
pytest -m "network"        # networkマークのテストのみ
```

## Tips 💡

### watchモード（ファイル変更を監視）
```bash
# pytest-watchが必要: pip install pytest-watch
ptw  # ファイル変更を検知して自動でテスト実行
```

### VS Codeでの実行

1. **Python環境を設定**
   - `Cmd+Shift+P` → `Python: Select Interpreter`
   - `./venv/bin/python` を選択

2. **Testingパネルを開く**
   - サイドバーのビーカーアイコンをクリック
   - Configure Python Tests を選択
   - pytest を選択
   - test_EchonetLite_for3.10 を選択

3. **テストを実行**
   - テストがサイドバーに表示されるので、クリックで実行可能！
   - 個別テストや全体実行が GUI でできるよ

### GitHub Actionsとの連携例
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          cd v0
          pip install -e ".[dev]"
      - name: Run tests
        run: |
          cd v0
          pytest --cov --cov-report=xml
```

## 🔧 トラブルシューティング

### venvが作成されない場合
```bash
# python3-venvパッケージが必要（Ubuntu/Debianの場合）
sudo apt-get install python3-venv

# macOSの場合、python3がインストールされているか確認
python3 --version
```

### インポートエラーが出る場合
```bash
# 仮想環境が有効化されているか確認
which python
# -> test_EchonetLite_for3.10/venv/bin/python と表示されればOK

# 仮想環境を再度有効化
source venv/bin/activate
```

### pytestが見つからない場合
```bash
# 仮想環境を有効化してから確認
source venv/bin/activate
pip list | grep pytest

# インストールされていなければ再インストール
pip install pytest pytest-cov pytest-mock
```

### テストがimportエラーになる場合
```bash
# パスが通っているか確認（venv有効化後）
python -c "import sys; import os; print(os.path.join(os.getcwd(), '..'))"

# conftest.pyでパスを追加しているので通常は問題なし
```

### venvを削除したい場合
```bash
# test_EchonetLite_for3.10ディレクトリで
rm -rf venv
# その後、./setup.sh で再作成
```

## お問い合わせ

問題が発生した場合は、GitHubのIssueで報告してください！
