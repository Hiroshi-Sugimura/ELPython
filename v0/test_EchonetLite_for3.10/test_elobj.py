#!/usr/bin/python3
"""
ELOBJクラスの単体テスト
"""

import pytest
from EchonetLite import ELOBJ, PDCEDT


class TestELOBJInit:
    """ELOBJの初期化テスト"""

    def test_init_default(self):
        """デフォルトコンストラクタのテスト"""
        elobj = ELOBJ()
        assert elobj.pdcedts == {}
        assert elobj.inf_property_map_raw == []
        assert elobj.set_property_map_raw == []
        assert elobj.get_property_map_raw == []

    def test_init_copy_constructor(self):
        """コピーコンストラクタのテスト"""
        original = ELOBJ()
        original.SetEDT(0x80, [0x30])
        original.SetMyPropertyMap(0x9d, [0x80])

        copy = ELOBJ(original)

        # 値が同じことを確認
        assert copy.pdcedts[0x80].edt == original.pdcedts[0x80].edt
        assert copy.inf_property_map_raw == original.inf_property_map_raw

        # ディープコピーの確認
        copy.SetEDT(0x80, [0x31])
        assert original.pdcedts[0x80].edt == [0x30]  # 元は変わらない
        assert copy.pdcedts[0x80].edt == [0x31]


class TestELOBJSetEDT:
    """SetEDTメソッドのテスト"""

    def test_set_edt_new_property(self):
        """新規プロパティの設定テスト"""
        elobj = ELOBJ()
        pdcedt = elobj.SetEDT(0x80, [0x30])

        assert pdcedt is not None
        assert pdcedt.pdc == 1
        assert pdcedt.edt == [0x30]
        assert elobj.pdcedts[0x80] == pdcedt

    def test_set_edt_overwrite(self):
        """既存プロパティの上書きテスト"""
        elobj = ELOBJ()
        elobj.SetEDT(0x80, [0x30])
        pdcedt = elobj.SetEDT(0x80, [0x31])

        assert pdcedt.edt == [0x31]
        assert elobj.pdcedts[0x80].edt == [0x31]

    def test_set_edt_multiple_properties(self):
        """複数プロパティの設定テスト"""
        elobj = ELOBJ()
        elobj.SetEDT(0x80, [0x30])
        elobj.SetEDT(0x81, [0x00])
        elobj.SetEDT(0x82, [0x01, 0x0d, 0x01, 0x00])

        assert 0x80 in elobj.pdcedts
        assert 0x81 in elobj.pdcedts
        assert 0x82 in elobj.pdcedts
        assert elobj.pdcedts[0x80].edt == [0x30]
        assert elobj.pdcedts[0x81].edt == [0x00]
        assert elobj.pdcedts[0x82].edt == [0x01, 0x0d, 0x01, 0x00]


class TestELOBJSetPDCEDT:
    """SetPDCEDTメソッドのテスト"""

    def test_set_pdcedt_with_object(self):
        """PDCEDTオブジェクトでの設定テスト"""
        elobj = ELOBJ()
        pdcedt = PDCEDT([0x01, 0x30])
        result = elobj.SetPDCEDT(0x80, pdcedt)

        assert result.edt == [0x30]
        assert elobj.pdcedts[0x80].edt == [0x30]

    def test_set_pdcedt_with_list(self):
        """リストでの設定テスト"""
        elobj = ELOBJ()
        result = elobj.SetPDCEDT(0x80, [0x01, 0x31])

        assert result.pdc == 0x01
        assert result.edt == [0x31]
        assert elobj.pdcedts[0x80].edt == [0x31]

    def test_set_pdcedt_empty_edt(self):
        """空EDTの設定テスト"""
        elobj = ELOBJ()
        result = elobj.SetPDCEDT(0x80, [0x00])

        assert result.pdc == 0
        assert result.edt == []


class TestELOBJGetPDCEDT:
    """GetPDCEDTメソッドのテスト"""

    def test_get_pdcedt_existing(self):
        """存在するプロパティの取得テスト"""
        elobj = ELOBJ()
        elobj.SetEDT(0x80, [0x30])

        pdcedt = elobj.GetPDCEDT(0x80)
        assert pdcedt is not None
        assert pdcedt.edt == [0x30]

    def test_get_pdcedt_non_existing(self):
        """存在しないプロパティの取得テスト"""
        elobj = ELOBJ()
        pdcedt = elobj.GetPDCEDT(0x99)
        assert pdcedt is None


class TestELOBJArrayAccess:
    """配列アクセス演算子のテスト"""

    def test_getitem_existing(self):
        """__getitem__で存在するプロパティを取得"""
        elobj = ELOBJ()
        elobj.SetEDT(0x80, [0x30])

        pdcedt = elobj[0x80]
        assert pdcedt is not None
        assert pdcedt.edt == [0x30]

    def test_getitem_non_existing(self):
        """__getitem__で存在しないプロパティを取得"""
        elobj = ELOBJ()
        pdcedt = elobj[0x99]
        assert pdcedt is None

    def test_setitem(self):
        """__setitem__でプロパティを設定"""
        elobj = ELOBJ()
        pdcedt = PDCEDT([0x01, 0x31])
        elobj[0x80] = pdcedt

        assert elobj.pdcedts[0x80].edt == [0x31]


class TestELOBJPropertyMap:
    """プロパティマップ関連のテスト"""

    def test_set_property_map_inf_format1(self):
        """INFプロパティマップ(形式1)の設定テスト"""
        elobj = ELOBJ()
        epc_list = [0x80, 0x81, 0x82]
        result = elobj.SetMyPropertyMap(0x9d, epc_list)

        assert result is not None
        # 元のepc_listはSetMyPropertyMap内で変更されている(個数が先頭に追加される)
        # 形式1: 最初のバイトが個数、続いてEPC
        assert result.edt[0] == 3  # 個数
        assert result.edt[1:4] == [0x80, 0x81, 0x82]

    def test_set_property_map_set_format1(self):
        """SETプロパティマップ(形式1)の設定テスト"""
        elobj = ELOBJ()
        epc_list = [0x80, 0x81]
        result = elobj.SetMyPropertyMap(0x9e, epc_list)

        assert result is not None
        # 元のepc_listはSetMyPropertyMap内で変更されている
        assert result.edt[0] == 2
        assert result.edt[1:3] == [0x80, 0x81]

    def test_set_property_map_get_format1(self):
        """GETプロパティマップ(形式1)の設定テスト"""
        elobj = ELOBJ()
        epc_list = [0x80, 0x81, 0x82, 0x88]
        result = elobj.SetMyPropertyMap(0x9f, epc_list)

        assert result is not None
        assert elobj.get_property_map_raw == epc_list
        assert result.edt[0] == 4

    def test_set_property_map_format2(self):
        """プロパティマップ(形式2、16個以上)の設定テスト"""
        elobj = ELOBJ()
        # 16個以上のプロパティ
        epc_list = [0x80, 0x81, 0x82, 0x83, 0x84, 0x90, 0x91, 0x92,
                    0x93, 0x94, 0xa1, 0xa2, 0xb1, 0xb2, 0xb3, 0xb4]
        result = elobj.SetMyPropertyMap(0x9f, epc_list)

        assert result is not None
        assert elobj.get_property_map_raw == epc_list
        # 形式2: 最初のバイトが個数、続いて17バイトのビットマップ
        assert result.edt[0] == 16
        assert len(result.edt) == 17  # 個数(1) + ビットマップ(16)

    def test_get_property_map_inf(self):
        """INFプロパティマップの取得テスト"""
        elobj = ELOBJ()
        epc_list = [0x80, 0xd5]
        elobj.SetMyPropertyMap(0x9d, epc_list)

        result = elobj.GetMyPropertyMap(0x9d)
        assert result == epc_list

    def test_get_property_map_set(self):
        """SETプロパティマップの取得テスト"""
        elobj = ELOBJ()
        epc_list = [0x80]
        elobj.SetMyPropertyMap(0x9e, epc_list)

        result = elobj.GetMyPropertyMap(0x9e)
        assert result == epc_list

    def test_get_property_map_get(self):
        """GETプロパティマップの取得テスト"""
        elobj = ELOBJ()
        epc_list = [0x80, 0x82, 0x83]
        elobj.SetMyPropertyMap(0x9f, epc_list)

        result = elobj.GetMyPropertyMap(0x9f)
        assert result == epc_list

    def test_get_property_map_invalid_epc(self):
        """無効なEPCでのプロパティマップ取得テスト"""
        elobj = ELOBJ()
        result = elobj.GetMyPropertyMap(0x99)
        assert result is None

    def test_set_property_map_invalid_epc(self):
        """無効なEPCでのプロパティマップ設定テスト"""
        elobj = ELOBJ()
        result = elobj.SetMyPropertyMap(0x99, [0x80])
        assert result is None


class TestELOBJHasProperty:
    """hasXXXPropertyメソッドのテスト"""

    def test_has_inf_property(self):
        """INFプロパティ保持チェックのテスト"""
        elobj = ELOBJ()
        elobj.SetMyPropertyMap(0x9d, [0x80, 0xd5])

        assert elobj.hasInfProperty(0x80) == True
        assert elobj.hasInfProperty(0xd5) == True
        assert elobj.hasInfProperty(0x81) == False

    def test_has_set_property(self):
        """SETプロパティ保持チェックのテスト"""
        elobj = ELOBJ()
        elobj.SetMyPropertyMap(0x9e, [0x80, 0x81])

        assert elobj.hasSetProperty(0x80) == True
        assert elobj.hasSetProperty(0x81) == True
        assert elobj.hasSetProperty(0x82) == False

    def test_has_get_property(self):
        """GETプロパティ保持チェックのテスト"""
        elobj = ELOBJ()
        elobj.SetMyPropertyMap(0x9f, [0x80, 0x82, 0x83, 0x88])

        assert elobj.hasGetProperty(0x80) == True
        assert elobj.hasGetProperty(0x88) == True
        assert elobj.hasGetProperty(0x90) == False


class TestELOBJEquality:
    """等価演算子のテスト"""

    def test_equality_empty(self):
        """空のELOBJ同士の比較テスト"""
        elobj1 = ELOBJ()
        elobj2 = ELOBJ()
        assert elobj1 == elobj2

    def test_equality_same_properties(self):
        """同じプロパティを持つELOBJの比較テスト"""
        elobj1 = ELOBJ()
        elobj1.SetEDT(0x80, [0x30])
        elobj1.SetMyPropertyMap(0x9d, [0x80])

        elobj2 = ELOBJ()
        elobj2.SetEDT(0x80, [0x30])
        elobj2.SetMyPropertyMap(0x9d, [0x80])

        assert elobj1 == elobj2

    def test_equality_different_properties(self):
        """異なるプロパティを持つELOBJの比較テスト"""
        elobj1 = ELOBJ()
        elobj1.SetEDT(0x80, [0x30])

        elobj2 = ELOBJ()
        elobj2.SetEDT(0x80, [0x31])

        assert not (elobj1 == elobj2)

    def test_equality_different_property_maps(self):
        """異なるプロパティマップを持つELOBJの比較テスト"""
        elobj1 = ELOBJ()
        elobj1.SetMyPropertyMap(0x9d, [0x80])

        elobj2 = ELOBJ()
        elobj2.SetMyPropertyMap(0x9d, [0x80, 0x81])

        assert not (elobj1 == elobj2)

    def test_equality_with_non_elobj(self):
        """ELOBJ以外との比較テスト"""
        elobj = ELOBJ()
        result = elobj.__eq__({})
        assert result == NotImplemented


class TestELOBJRealWorldScenarios:
    """実際の使用シナリオのテスト"""

    def test_controller_object(self):
        """コントローラオブジェクトのテスト"""
        controller = ELOBJ()
        controller.SetEDT(0x80, [0x30])  # 動作状態: ON
        controller.SetEDT(0x81, [0x00])  # 設置場所
        controller.SetEDT(0x88, [0x42])  # 異常状態なし
        controller.SetMyPropertyMap(0x9d, [0x80, 0xd6, 0x88])  # INF
        controller.SetMyPropertyMap(0x9e, [0x80, 0x81])        # SET
        controller.SetMyPropertyMap(0x9f, [0x80, 0x81, 0x82, 0x83, 0x88, 0x8a, 0x9d, 0x9e, 0x9f])  # GET

        assert controller[0x80] is not None
        assert controller[0x80].edt == [0x30]
        assert controller.hasInfProperty(0x80) == True
        assert controller.hasSetProperty(0x80) == True
        assert controller.hasGetProperty(0x80) == True

    def test_node_profile_object(self):
        """ノードプロファイルオブジェクトのテスト"""
        node_profile = ELOBJ()
        node_profile.SetEDT(0x80, [0x30])
        node_profile.SetEDT(0x82, [0x01, 0x0d, 0x01, 0x00])  # Ver 1.13
        node_profile.SetEDT(0xd3, [0x00, 0x00, 0x01])       # 総インスタンス数
        node_profile.SetMyPropertyMap(0x9d, [0x80, 0xd5])
        node_profile.SetMyPropertyMap(0x9e, [0x80])
        node_profile.SetMyPropertyMap(0x9f, [0x80, 0x82, 0x83, 0x88, 0x8a, 0x9d, 0x9e, 0x9f, 0xd3, 0xd4, 0xd5, 0xd6, 0xd7])

        assert node_profile[0x82] is not None
        assert node_profile[0x82].edt == [0x01, 0x0d, 0x01, 0x00]
        assert node_profile.hasInfProperty(0xd5) == True
        assert node_profile.hasGetProperty(0xd3) == True

    def test_general_lighting_object(self):
        """一般照明オブジェクトのテスト"""
        lighting = ELOBJ()
        lighting.SetEDT(0x80, [0x30])  # 動作状態: ON
        lighting.SetEDT(0xb0, [0x64])  # 照度レベル: 100%
        lighting.SetMyPropertyMap(0x9d, [0x80])
        lighting.SetMyPropertyMap(0x9e, [0x80, 0xb0])
        lighting.SetMyPropertyMap(0x9f, [0x80, 0xb0])

        assert lighting[0xb0] is not None
        assert lighting[0xb0].edt == [0x64]
        assert lighting.hasSetProperty(0xb0) == True
        assert lighting.hasGetProperty(0xb0) == True

    def test_property_update_scenario(self):
        """プロパティ更新シナリオのテスト"""
        device = ELOBJ()
        device.SetEDT(0x80, [0x31])  # OFF

        # ONに変更
        device.SetEDT(0x80, [0x30])
        assert device[0x80].edt == [0x30]

        # 再びOFFに変更
        device.SetEDT(0x80, [0x31])
        assert device[0x80].edt == [0x31]


class TestELOBJEdgeCases:
    """エッジケースのテスト"""

    def test_many_properties(self):
        """多数のプロパティを持つオブジェクトのテスト"""
        elobj = ELOBJ()

        # 多数のプロパティを設定
        for epc in range(0x80, 0xc0):
            elobj.SetEDT(epc, [epc])

        # すべて正しく設定されているか確認
        for epc in range(0x80, 0xc0):
            assert elobj[epc] is not None
            assert elobj[epc].edt == [epc]

    def test_property_map_format_boundary(self):
        """プロパティマップの形式境界(15個→16個)のテスト"""
        elobj = ELOBJ()

        # 15個(形式1の最大)
        epc_list_15 = list(range(0x80, 0x8f))
        result = elobj.SetMyPropertyMap(0x9f, epc_list_15)
        assert result.edt[0] == 15
        assert len(result.edt) == 16  # 個数(1) + EPC(15)

        # 16個(形式2に切り替わる)
        epc_list_16 = list(range(0x80, 0x90))
        result = elobj.SetMyPropertyMap(0x9f, epc_list_16)
        assert result.edt[0] == 16
        assert len(result.edt) == 17  # 個数(1) + ビットマップ(16)


class TestELOBJErrorCases:
    """エラーケースとバリデーションのテスト"""

    def test_setEDT_with_invalid_epc_type(self):
        """SetEDTに無効なEPC型を渡すエラーテスト"""
        elobj = ELOBJ()

        with pytest.raises(Exception):
            elobj.SetEDT("invalid", [0x30])

        with pytest.raises(Exception):
            elobj.SetEDT(None, [0x30])

        with pytest.raises(Exception):
            elobj.SetEDT([0x80], [0x30])

    def test_setEDT_with_invalid_edt_type(self):
        """SetEDTに無効なEDT型を渡すエラーテスト"""
        elobj = ELOBJ()

        with pytest.raises(Exception):
            elobj.SetEDT(0x80, "invalid")

        with pytest.raises(Exception):
            elobj.SetEDT(0x80, 123)

        with pytest.raises(Exception):
            elobj.SetEDT(0x80, None)

    def test_setEDT_with_out_of_range_epc(self):
        """範囲外のEPCでのSetEDTエラーテスト"""
        elobj = ELOBJ()

        # 負の値
        with pytest.raises(Exception):
            elobj.SetEDT(-1, [0x30])

        # 0xFFを超える値
        with pytest.raises(Exception):
            elobj.SetEDT(256, [0x30])

    def test_setEDT_with_invalid_edt_values(self):
        """SetEDTに範囲外のEDT値を渡すエラーテスト"""
        elobj = ELOBJ()

        with pytest.raises(Exception):
            elobj.SetEDT(0x80, [-1])

        with pytest.raises(Exception):
            elobj.SetEDT(0x80, [256])

    def test_setPDCEDT_with_invalid_type(self):
        """SetPDCEDTに無効な型を渡すエラーテスト"""
        elobj = ELOBJ()

        with pytest.raises(Exception):
            elobj.SetPDCEDT(0x80, "invalid")

        with pytest.raises(Exception):
            elobj.SetPDCEDT(0x80, 123)

        with pytest.raises(Exception):
            elobj.SetPDCEDT(0x80, None)

    def test_setPDCEDT_with_invalid_epc(self):
        """SetPDCEDTに無効なEPCを渡すエラーテスト"""
        elobj = ELOBJ()
        pdcedt = PDCEDT([0x01, 0x30])

        with pytest.raises(Exception):
            elobj.SetPDCEDT("invalid", pdcedt)

        with pytest.raises(Exception):
            elobj.SetPDCEDT(None, pdcedt)

    def test_getitem_with_invalid_type(self):
        """__getitem__に無効な型を渡すエラーテスト"""
        elobj = ELOBJ()

        with pytest.raises(Exception):
            _ = elobj["invalid"]

        with pytest.raises(Exception):
            _ = elobj[None]

    def test_setitem_with_invalid_type(self):
        """__setitem__に無効な型を渡すエラーテスト"""
        elobj = ELOBJ()
        pdcedt = PDCEDT([0x01, 0x30])

        with pytest.raises(Exception):
            elobj["invalid"] = pdcedt

        with pytest.raises(Exception):
            elobj[None] = pdcedt

    def test_setitem_with_invalid_value_type(self):
        """__setitem__に無効な値型を渡すエラーテスト"""
        elobj = ELOBJ()

        with pytest.raises(Exception):
            elobj[0x80] = "invalid"

        with pytest.raises(Exception):
            elobj[0x80] = 123

        with pytest.raises(Exception):
            elobj[0x80] = None

    def test_setMyPropertyMap_with_invalid_epc(self):
        """SetMyPropertyMapに無効なEPCを渡すエラーテスト"""
        elobj = ELOBJ()

        # 0x9d, 0x9e, 0x9f以外は無効
        result = elobj.SetMyPropertyMap(0x80, [0x80])
        assert result is None

        result = elobj.SetMyPropertyMap(0x9c, [0x80])
        assert result is None

        result = elobj.SetMyPropertyMap(0xa0, [0x80])
        assert result is None

    def test_setMyPropertyMap_with_invalid_list_type(self):
        """SetMyPropertyMapに無効なリスト型を渡すエラーテスト"""
        elobj = ELOBJ()

        with pytest.raises(Exception):
            elobj.SetMyPropertyMap(0x9d, "invalid")

        with pytest.raises(Exception):
            elobj.SetMyPropertyMap(0x9d, 123)

        with pytest.raises(Exception):
            elobj.SetMyPropertyMap(0x9d, None)

    def test_setMyPropertyMap_with_invalid_list_values(self):
        """SetMyPropertyMapに無効なリスト値を渡すエラーテスト"""
        elobj = ELOBJ()

        with pytest.raises(Exception):
            elobj.SetMyPropertyMap(0x9d, [-1, 0x80])

        with pytest.raises(Exception):
            elobj.SetMyPropertyMap(0x9d, [256, 0x80])

        with pytest.raises(Exception):
            elobj.SetMyPropertyMap(0x9d, [0x80, "invalid"])

    def test_getMyPropertyMap_with_invalid_epc(self):
        """GetMyPropertyMapに無効なEPCを渡すテスト"""
        elobj = ELOBJ()

        result = elobj.GetMyPropertyMap(0x80)
        assert result is None

        result = elobj.GetMyPropertyMap(0x9c)
        assert result is None

    def test_hasInfProperty_with_invalid_type(self):
        """hasInfPropertyに無効な型を渡すエラーテスト"""
        elobj = ELOBJ()
        elobj.SetMyPropertyMap(0x9d, [0x80])

        with pytest.raises(Exception):
            elobj.hasInfProperty("invalid")

        with pytest.raises(Exception):
            elobj.hasInfProperty(None)

    def test_hasSetProperty_with_invalid_type(self):
        """hasSetPropertyに無効な型を渡すエラーテスト"""
        elobj = ELOBJ()
        elobj.SetMyPropertyMap(0x9e, [0x80])

        with pytest.raises(Exception):
            elobj.hasSetProperty("invalid")

        with pytest.raises(Exception):
            elobj.hasSetProperty(None)

    def test_hasGetProperty_with_invalid_type(self):
        """hasGetPropertyに無効な型を渡すエラーテスト"""
        elobj = ELOBJ()
        elobj.SetMyPropertyMap(0x9f, [0x80])

        with pytest.raises(Exception):
            elobj.hasGetProperty("invalid")

        with pytest.raises(Exception):
            elobj.hasGetProperty(None)

    def test_equality_with_invalid_type(self):
        """等価比較に無効な型を渡すテスト"""
        elobj = ELOBJ()

        assert elobj.__eq__(None) == NotImplemented
        assert elobj.__eq__("string") == NotImplemented
        assert elobj.__eq__(123) == NotImplemented
        assert elobj.__eq__([]) == NotImplemented

    def test_copy_constructor_with_invalid_type(self):
        """コピーコンストラクタに無効な型を渡すエラーテスト"""
        with pytest.raises(Exception):
            ELOBJ("not an ELOBJ")

        with pytest.raises(Exception):
            ELOBJ({})

        with pytest.raises(Exception):
            ELOBJ([])

    def test_boundary_epc_values(self):
        """境界値のEPCテスト"""
        elobj = ELOBJ()

        # 0x00
        result = elobj.SetEDT(0x00, [0x30])
        assert result is not None

        # 0xFF
        result = elobj.SetEDT(0xff, [0x30])
        assert result is not None

    def test_empty_property_map(self):
        """空のプロパティマップのテスト"""
        elobj = ELOBJ()

        # 空リストで設定
        result = elobj.SetMyPropertyMap(0x9d, [])
        assert result is not None
        assert result.edt[0] == 0  # 個数は0

        # 空の状態で検索
        assert elobj.hasInfProperty(0x80) == False

    def test_property_overwrite_consistency(self):
        """プロパティ上書き時の一貫性テスト"""
        elobj = ELOBJ()

        # 初回設定
        elobj.SetEDT(0x80, [0x30])
        original_pdcedt = elobj[0x80]

        # 上書き
        elobj.SetEDT(0x80, [0x31])
        new_pdcedt = elobj[0x80]

        # 参照が更新されていることを確認
        assert new_pdcedt.edt == [0x31]
        # 元のPDCEDTオブジェクトは変更されない(新しいオブジェクトが作られる)
        assert original_pdcedt.edt == [0x30]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
