#!/bin/bash

# テスト実行スクリプト
# 使い方: ./run_tests.sh [pytest options]

# スクリプトのディレクトリに移動
cd "$(dirname "$0")"

# venvが存在しない場合
if [ ! -d "venv" ]; then
    echo "❌ venvが見つかりません"
    echo "先に setup.sh を実行してください:"
    echo "  chmod +x setup.sh"
    echo "  ./setup.sh"
    exit 1
fi

# venvを有効化
source venv/bin/activate

# pytestが利用可能かチェック
if ! command -v pytest &> /dev/null; then
    echo "❌ pytestが見つかりません"
    echo "先に setup.sh を実行してください"
    exit 1
fi

# テスト実行
echo "🧪 テストを実行中..."
echo ""

# 引数があればそのまま渡す、なければデフォルトオプション
if [ $# -eq 0 ]; then
    pytest -v
else
    pytest "$@"
fi

# 終了コードを保存
exit_code=$?

# venvを無効化
deactivate

exit $exit_code
