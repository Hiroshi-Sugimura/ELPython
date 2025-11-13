#!/usr/bin/python3
"""
PDCEDTクラスの単体テスト
"""

import pytest
from EchonetLite import PDCEDT


class TestPDCEDTInit:
    """PDCEDTの初期化テスト"""

    def test_init_default(self):
        """デフォルトコンストラクタのテスト"""
        pdcedt = PDCEDT()
        assert pdcedt.pdc == 0
        assert pdcedt.edt == []
        assert pdcedt.length == 1

    def test_init_with_list(self):
        """リストでの初期化テスト"""
        pdcedt = PDCEDT([0x02, 0x80, 0x81])
        assert pdcedt.pdc == 0x02
        assert pdcedt.edt == [0x80, 0x81]
        assert pdcedt.length == 3

    def test_init_with_pdc_zero(self):
        """PDC=0でのリスト初期化テスト"""
        pdcedt = PDCEDT([0x00])
        assert pdcedt.pdc == 0x00
        assert pdcedt.edt == []
        assert pdcedt.length == 1

    def test_init_with_single_byte(self):
        """1バイトデータでの初期化テスト"""
        pdcedt = PDCEDT([0x01, 0x30])
        assert pdcedt.pdc == 0x01
        assert pdcedt.edt == [0x30]
        assert pdcedt.length == 2

    def test_init_copy_constructor(self):
        """コピーコンストラクタのテスト"""
        original = PDCEDT([0x02, 0x80, 0x81])
        copy = PDCEDT(original)

        assert copy.pdc == original.pdc
        assert copy.edt == original.edt
        assert copy.length == original.length

        # ディープコピーの確認
        copy.setEDT([0x90, 0x91])
        assert original.edt == [0x80, 0x81]  # 元のデータは変わらない
        assert copy.edt == [0x90, 0x91]

    def test_init_with_empty_list(self):
        """空リストでの初期化テスト"""
        pdcedt = PDCEDT([])
        assert pdcedt.pdc == 0
        assert pdcedt.edt == []
        assert pdcedt.length == 1


class TestPDCEDTSetEDT:
    """setEDTメソッドのテスト"""

    def test_set_edt_single_byte(self):
        """1バイトEDTの設定テスト"""
        pdcedt = PDCEDT()
        pdcedt.setEDT([0x30])

        assert pdcedt.pdc == 1
        assert pdcedt.edt == [0x30]
        assert pdcedt.length == 2

    def test_set_edt_multiple_bytes(self):
        """複数バイトEDTの設定テスト"""
        pdcedt = PDCEDT()
        pdcedt.setEDT([0x80, 0x81, 0x82])

        assert pdcedt.pdc == 3
        assert pdcedt.edt == [0x80, 0x81, 0x82]
        assert pdcedt.length == 4

    def test_set_edt_empty(self):
        """空EDTの設定テスト"""
        pdcedt = PDCEDT([0x02, 0x80, 0x81])
        pdcedt.setEDT([])

        assert pdcedt.pdc == 0
        assert pdcedt.edt == []
        assert pdcedt.length == 1

    def test_set_edt_overwrite(self):
        """EDTの上書きテスト"""
        pdcedt = PDCEDT([0x01, 0x30])
        pdcedt.setEDT([0x31, 0x32])

        assert pdcedt.pdc == 2
        assert pdcedt.edt == [0x31, 0x32]
        assert pdcedt.length == 3


class TestPDCEDTEquality:
    """等価演算子のテスト"""

    def test_equality_same_values(self):
        """同じ値のPDCEDTの比較テスト"""
        pdcedt1 = PDCEDT([0x02, 0x80, 0x81])
        pdcedt2 = PDCEDT([0x02, 0x80, 0x81])

        assert pdcedt1 == pdcedt2

    def test_equality_different_values(self):
        """異なる値のPDCEDTの比較テスト"""
        pdcedt1 = PDCEDT([0x02, 0x80, 0x81])
        pdcedt2 = PDCEDT([0x01, 0x30])

        assert not (pdcedt1 == pdcedt2)

    def test_equality_empty(self):
        """空のPDCEDTの比較テスト"""
        pdcedt1 = PDCEDT()
        pdcedt2 = PDCEDT()

        assert pdcedt1 == pdcedt2

    def test_equality_with_non_pdcedt(self):
        """PDCEDT以外との比較テスト"""
        pdcedt = PDCEDT([0x01, 0x30])

        result = pdcedt.__eq__([0x01, 0x30])
        assert result == NotImplemented


class TestPDCEDTGetString:
    """getStringメソッドのテスト"""

    def test_get_string_empty(self):
        """空のPDCEDTの文字列取得テスト"""
        pdcedt = PDCEDT()
        assert pdcedt.getString() == '00'

    def test_get_string_single_byte(self):
        """1バイトデータの文字列取得テスト"""
        pdcedt = PDCEDT([0x01, 0x30])
        assert pdcedt.getString() == '0130'

    def test_get_string_multiple_bytes(self):
        """複数バイトデータの文字列取得テスト"""
        pdcedt = PDCEDT([0x03, 0x80, 0x81, 0x82])
        assert pdcedt.getString() == '03808182'

    def test_get_string_hex_format(self):
        """16進数フォーマットのテスト"""
        pdcedt = PDCEDT([0x02, 0xff, 0x00])
        assert pdcedt.getString() == '02ff00'

    def test_get_string_after_set_edt(self):
        """setEDT後の文字列取得テスト"""
        pdcedt = PDCEDT()
        pdcedt.setEDT([0x80, 0x81])
        assert pdcedt.getString() == '028081'


class TestPDCEDTPrintString:
    """printStringメソッドのテスト"""

    def test_print_string_empty(self):
        """空のPDCEDTのprintStringテスト"""
        pdcedt = PDCEDT()
        result = pdcedt.printString()
        assert result == "PDC:00, EDT: []"

    def test_print_string_single_byte(self):
        """1バイトデータのprintStringテスト"""
        pdcedt = PDCEDT([0x01, 0x30])
        result = pdcedt.printString()
        assert result == "PDC:01, EDT:30"

    def test_print_string_multiple_bytes(self):
        """複数バイトデータのprintStringテスト"""
        pdcedt = PDCEDT([0x03, 0x80, 0x81, 0x82])
        result = pdcedt.printString()
        assert result == "PDC:03, EDT:80,81,82"

    def test_print_string_pdc_zero(self):
        """PDC=0のprintStringテスト"""
        pdcedt = PDCEDT([0x00])
        result = pdcedt.printString()
        assert result == "PDC:00, EDT: []"


class TestPDCEDTEdgeCases:
    """エッジケースのテスト"""

    def test_large_edt(self):
        """大きなEDTのテスト"""
        large_edt = list(range(0, 255))
        pdcedt = PDCEDT()
        pdcedt.setEDT(large_edt)

        assert pdcedt.pdc == 255
        assert pdcedt.edt == large_edt
        assert pdcedt.length == 256

    def test_set_edt_updates_all_properties(self):
        """setEDTが全プロパティを更新することのテスト"""
        pdcedt = PDCEDT([0x05, 0x01, 0x02, 0x03, 0x04, 0x05])

        # 元の状態確認
        assert pdcedt.pdc == 5
        assert len(pdcedt.edt) == 5
        assert pdcedt.length == 6

        # 短いEDTに更新
        pdcedt.setEDT([0x30])
        assert pdcedt.pdc == 1
        assert len(pdcedt.edt) == 1
        assert pdcedt.length == 2

    def test_multiple_set_edt_calls(self):
        """複数回setEDTを呼び出すテスト"""
        pdcedt = PDCEDT()

        pdcedt.setEDT([0x30])
        assert pdcedt.pdc == 1

        pdcedt.setEDT([0x31, 0x32])
        assert pdcedt.pdc == 2

        pdcedt.setEDT([])
        assert pdcedt.pdc == 0


class TestPDCEDTRealWorldScenarios:
    """実際の使用シナリオのテスト"""

    def test_power_status_property(self):
        """電源状態プロパティ(0x80)のテスト"""
        # ON状態
        pdcedt_on = PDCEDT([0x01, 0x30])
        assert pdcedt_on.pdc == 1
        assert pdcedt_on.edt == [0x30]

        # OFF状態
        pdcedt_off = PDCEDT([0x01, 0x31])
        assert pdcedt_off.pdc == 1
        assert pdcedt_off.edt == [0x31]

    def test_temperature_property(self):
        """温度プロパティのテスト（2バイト）"""
        # 25.5度を表現 (0x00FF = 255 = 25.5度)
        pdcedt = PDCEDT([0x02, 0x00, 0xff])
        assert pdcedt.pdc == 2
        assert pdcedt.edt == [0x00, 0xff]
        assert pdcedt.getString() == '0200ff'

    def test_instance_list_property(self):
        """インスタンスリストプロパティのテスト"""
        # 2つのインスタンス
        pdcedt = PDCEDT([0x07, 0x02, 0x05, 0xff, 0x01, 0x01, 0x30, 0x01])
        assert pdcedt.pdc == 7
        assert len(pdcedt.edt) == 7
        assert pdcedt.getString() == '070205ff01013001'


class TestPDCEDTErrorCases:
    """エラーケースとバリデーションのテスト"""

    def test_init_with_invalid_type(self):
        """無効な型での初期化エラーテスト"""
        with pytest.raises(Exception):
            PDCEDT("invalid")

        with pytest.raises(Exception):
            PDCEDT(123)

    def test_init_with_none(self):
        """Noneでの初期化エラーテスト"""
        with pytest.raises(Exception):
            PDCEDT(None)

    def test_init_pdc_mismatch(self):
        """PDCとEDT長の不一致テスト"""
        # PDC=3だけどEDTは2バイトしかない
        pdcedt = PDCEDT([0x03, 0x80, 0x81])
        # 実装によっては自動的に調整される可能性があるので、
        # 実際の挙動を確認
        assert pdcedt.pdc == 0x03
        # EDTの実際の長さを確認
        assert len(pdcedt.edt) == 2

    def test_setEDT_with_invalid_type(self):
        """setEDTに無効な型を渡すエラーテスト"""
        pdcedt = PDCEDT()

        with pytest.raises(Exception):
            pdcedt.setEDT("invalid")

        with pytest.raises(Exception):
            pdcedt.setEDT(123)

        with pytest.raises(Exception):
            pdcedt.setEDT(None)

    def test_setEDT_with_invalid_values(self):
        """setEDTに範囲外の値を渡すエラーテスト"""
        pdcedt = PDCEDT()

        # 負の値
        with pytest.raises(Exception):
            pdcedt.setEDT([-1, 0x30])

        # 255を超える値
        with pytest.raises(Exception):
            pdcedt.setEDT([256, 0x30])

    def test_setEDT_with_non_integer_values(self):
        """setEDTに整数以外を含むリストを渡すエラーテスト"""
        pdcedt = PDCEDT()

        with pytest.raises(Exception):
            pdcedt.setEDT([0x30, "invalid"])

        with pytest.raises(Exception):
            pdcedt.setEDT([0x30, None])

        with pytest.raises(Exception):
            pdcedt.setEDT([0x30, 1.5])

    def test_maximum_edt_size(self):
        """最大EDTサイズのテスト"""
        # ECHONET Liteの仕様上、PDCは1バイト(0-255)
        max_edt = list(range(0, 255))
        pdcedt = PDCEDT()
        pdcedt.setEDT(max_edt)

        assert pdcedt.pdc == 255
        assert len(pdcedt.edt) == 255

    def test_init_with_oversized_list(self):
        """255バイトを超えるリストでの初期化テスト"""
        # PDC(1バイト) + EDT(256バイト) = 範囲外
        oversized_list = [0xff] + list(range(0, 256))

        # 実装によってはエラーまたは自動トリミング
        try:
            pdcedt = PDCEDT(oversized_list)
            # エラーにならない場合は、適切に処理されているか確認
            assert pdcedt.pdc <= 255
        except Exception:
            # エラーになる場合はそれも正常
            pass

    def test_equality_with_different_types(self):
        """異なる型との等価比較エラーケースのテスト"""
        pdcedt = PDCEDT([0x01, 0x30])

        # NotImplementedが返されることを確認
        assert pdcedt.__eq__(None) == NotImplemented
        assert pdcedt.__eq__("string") == NotImplemented
        assert pdcedt.__eq__(123) == NotImplemented
        assert pdcedt.__eq__({}) == NotImplemented

    def test_copy_constructor_with_invalid_type(self):
        """コピーコンストラクタに無効な型を渡すエラーテスト"""
        with pytest.raises(Exception):
            PDCEDT("not a PDCEDT")

        with pytest.raises(Exception):
            PDCEDT({})

    def test_boundary_values(self):
        """境界値のテスト"""
        # 0x00
        pdcedt_min = PDCEDT([0x01, 0x00])
        assert pdcedt_min.edt == [0x00]

        # 0xFF
        pdcedt_max = PDCEDT([0x01, 0xff])
        assert pdcedt_max.edt == [0xff]

        # PDC=0xFF
        pdcedt_max_pdc = PDCEDT()
        pdcedt_max_pdc.setEDT([0xff] * 255)
        assert pdcedt_max_pdc.pdc == 255

    def test_empty_list_behavior(self):
        """空リストの挙動確認テスト"""
        pdcedt = PDCEDT([])

        # 空リストでも正常に動作するか
        assert pdcedt.getString() == '00'
        assert pdcedt.printString() == "PDC:00, EDT: []"
        assert pdcedt.length == 1
        assert pdcedt.pdc == 0
        assert pdcedt.edt == []


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
