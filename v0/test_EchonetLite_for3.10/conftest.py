"""
pytestの共通設定とフィクスチャ
"""
import pytest
import sys
import os
import importlib.util

# EchonetLite_for3.10ディレクトリのパスを取得
echonet_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'EchonetLite_for3.10'))

# 直接ディレクトリをパスに追加（ドット付きフォルダ名問題を回避）
if echonet_dir not in sys.path:
    sys.path.insert(0, echonet_dir)

# EchonetLiteモジュールをインポート可能にする
# __init__.pyを使って、パッケージとしてロード
spec = importlib.util.spec_from_file_location("EchonetLite", os.path.join(echonet_dir, "__init__.py"))
EchonetLite_module = importlib.util.module_from_spec(spec)
sys.modules['EchonetLite'] = EchonetLite_module
spec.loader.exec_module(EchonetLite_module)

@pytest.fixture
def mock_socket(mocker):
    """ソケットをモック化するフィクスチャ"""
    return mocker.patch('socket.socket')

@pytest.fixture
def echonet_lite(mock_socket):
    """EchonetLiteインスタンスを返すフィクスチャ"""
    from EchonetLite import EchonetLite
    return EchonetLite()

@pytest.fixture
def pdcedt():
    """PDCEDTインスタンスを返すフィクスチャ"""
    from EchonetLite import PDCEDT
    return PDCEDT()

@pytest.fixture
def elobj():
    """ELOBJインスタンスを返すフィクスチャ"""
    from EchonetLite import ELOBJ
    return ELOBJ()
