"""
pytestの共通設定とフィクスチャ (Python 3.4 compatible version)
"""
import pytest
import sys
import os

# EchonetLite_for3.4(uPy)ディレクトリのパスを取得
echonet_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'EchonetLite_for3.4(uPy)'))

# 直接ディレクトリをパスに追加
if echonet_dir not in sys.path:
    sys.path.insert(0, echonet_dir)

@pytest.fixture
def mock_socket(mocker):
    """ソケットをモック化するフィクスチャ"""
    return mocker.patch('socket.socket')

@pytest.fixture
def echonet_lite(mocker, mock_socket):
    """EchonetLiteインスタンスを返すフィクスチャ"""
    from EchonetLite import EchonetLite
    # _get_local_ip()をモックしてテスト用のIPアドレスを返す
    mocker.patch.object(EchonetLite, '_get_local_ip', return_value='192.168.1.100')
    return EchonetLite()

@pytest.fixture
def pdcedt():
    """PDCEDTインスタンスを返すフィクスチャ"""
    from PDCEDT import PDCEDT
    return PDCEDT()

@pytest.fixture
def elobj():
    """ELOBJインスタンスを返すフィクスチャ"""
    from ELOBJ import ELOBJ
    return ELOBJ()
