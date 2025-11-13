#!/bin/bash

# テスト環境セットアップスクリプト
# 使い方: ./setup.sh

echo "🚀 EchonetLite テスト環境をセットアップ中..."
echo ""

# スクリプトのディレクトリに移動
cd "$(dirname "$0")"

# venvが既に存在するかチェック
if [ -d "venv" ]; then
    echo "⚠️  venvが既に存在します"
    read -p "削除して再作成しますか？ (y/N): " answer
    if [ "$answer" = "y" ] || [ "$answer" = "Y" ]; then
        echo "🗑️  既存のvenvを削除中..."
        rm -rf venv
    else
        echo "ℹ️  既存のvenvを使用します"
    fi
fi

# venvを作成
if [ ! -d "venv" ]; then
    echo "📦 仮想環境(venv)を作成中..."
    python3 -m venv venv

    if [ $? -ne 0 ]; then
        echo "❌ venvの作成に失敗しました"
        exit 1
    fi
fi

# venvを有効化
echo "🔌 仮想環境を有効化中..."
source venv/bin/activate

# pipをアップグレード
echo "⬆️  pipをアップグレード中..."
pip install --upgrade pip

# 依存パッケージをインストール
echo "📦 依存パッケージをインストール中..."
pip install pytest pytest-cov pytest-mock

if [ $? -ne 0 ]; then
    echo "❌ パッケージのインストールに失敗しました"
    exit 1
fi

echo ""
echo "✅ セットアップ完了！"
echo ""
echo "📝 使い方:"
echo ""
echo "1. 仮想環境を有効化:"
echo "   source venv/bin/activate"
echo ""
echo "2. テスト実行:"
echo "   pytest"
echo "   pytest -v                    # 詳細表示"
echo "   pytest --cov                 # カバレッジ付き"
echo "   pytest --cov --cov-report=html  # HTMLレポート"
echo ""
echo "3. 仮想環境を無効化:"
echo "   deactivate"
echo ""
