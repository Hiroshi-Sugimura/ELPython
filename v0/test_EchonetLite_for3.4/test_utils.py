#!/usr/bin/python3
"""!
@file test_utils.py
@brief utils.pyのユニットテスト (Python 3.4 compatible version)
@details deepcopy関連の共通ユーティリティ関数のテスト
"""

import pytest
from utils import deepcopy_list, deepcopy_dict_pdcedt
from PDCEDT import PDCEDT


class TestDeepcopyList:
    """deepcopy_list関数のテスト"""

    def test_deepcopy_list_normal(self):
        """通常のリストのコピー"""
        src = [1, 2, 3, 4, 5]
        dst = deepcopy_list(src)
        assert dst == src
        assert dst is not src  # 異なるオブジェクト
        # 元のリストを変更しても影響しない
        src[0] = 99
        assert dst[0] == 1

    def test_deepcopy_list_empty(self):
        """空リストのコピー"""
        src = []
        dst = deepcopy_list(src)
        assert dst == []
        assert dst is not src

    def test_deepcopy_list_none(self):
        """Noneの場合"""
        dst = deepcopy_list(None)
        assert dst == []

    def test_deepcopy_list_single_element(self):
        """要素1つのリスト"""
        src = [42]
        dst = deepcopy_list(src)
        assert dst == [42]
        assert dst is not src

    def test_deepcopy_list_large(self):
        """大きなリストのコピー"""
        src = list(range(1000))
        dst = deepcopy_list(src)
        assert dst == src
        assert dst is not src

    def test_deepcopy_list_all_zeros(self):
        """全て0のリスト"""
        src = [0, 0, 0, 0]
        dst = deepcopy_list(src)
        assert dst == [0, 0, 0, 0]
        assert dst is not src

    def test_deepcopy_list_boundary_values(self):
        """境界値のリスト"""
        src = [0, 255, 128]
        dst = deepcopy_list(src)
        assert dst == [0, 255, 128]
        assert dst is not src

    def test_deepcopy_list_independence(self):
        """コピー元とコピー先の独立性"""
        src = [10, 20, 30]
        dst = deepcopy_list(src)
        # コピー先を変更
        dst.append(40)
        dst[0] = 99
        # コピー元は変更されていない
        assert src == [10, 20, 30]
        assert dst == [99, 20, 30, 40]


class TestDeepcopyDictPdcedt:
    """deepcopy_dict_pdcedt関数のテスト"""

    def test_deepcopy_dict_empty(self):
        """空の辞書のコピー"""
        src = {}
        dst = deepcopy_dict_pdcedt(src)
        assert dst == {}
        assert dst is not src

    def test_deepcopy_dict_none(self):
        """Noneの場合"""
        dst = deepcopy_dict_pdcedt(None)
        assert dst == {}

    def test_deepcopy_dict_single_entry(self):
        """1つのエントリを持つ辞書"""
        src = {0x80: PDCEDT([1, 0x30])}
        dst = deepcopy_dict_pdcedt(src)

        assert 0x80 in dst
        assert dst[0x80] == src[0x80]
        assert dst[0x80] is not src[0x80]  # 異なるオブジェクト

    def test_deepcopy_dict_multiple_entries(self):
        """複数のエントリを持つ辞書"""
        src = {
            0x80: PDCEDT([1, 0x30]),
            0x81: PDCEDT([1, 0x00]),
            0x82: PDCEDT([3, 0x00, 0x00, 0x42])
        }
        dst = deepcopy_dict_pdcedt(src)

        assert len(dst) == 3
        assert 0x80 in dst
        assert 0x81 in dst
        assert 0x82 in dst

        # 値が等しい
        assert dst[0x80] == src[0x80]
        assert dst[0x81] == src[0x81]
        assert dst[0x82] == src[0x82]

        # 異なるオブジェクト
        assert dst[0x80] is not src[0x80]
        assert dst[0x81] is not src[0x81]
        assert dst[0x82] is not src[0x82]

    def test_deepcopy_dict_independence(self):
        """コピー元とコピー先の独立性"""
        src = {0x80: PDCEDT([1, 0x30])}
        dst = deepcopy_dict_pdcedt(src)

        # コピー元を変更
        src[0x80].setEDT([0x31])

        # コピー先は変更されていない
        assert dst[0x80].edt == [0x30]
        assert src[0x80].edt == [0x31]

    def test_deepcopy_dict_add_entry_to_copy(self):
        """コピー先に新しいエントリを追加"""
        src = {0x80: PDCEDT([1, 0x30])}
        dst = deepcopy_dict_pdcedt(src)

        # コピー先に追加
        dst[0x81] = PDCEDT([1, 0x00])

        # コピー元は変更されていない
        assert 0x81 not in src
        assert 0x81 in dst

    def test_deepcopy_dict_with_empty_pdcedt(self):
        """空のPDCEDTを含む辞書"""
        src = {0x80: PDCEDT([0])}
        dst = deepcopy_dict_pdcedt(src)

        assert 0x80 in dst
        assert dst[0x80] == src[0x80]
        assert dst[0x80].pdc == 0
        assert dst[0x80].edt == []

    def test_deepcopy_dict_with_large_edt(self):
        """大きなEDTを持つPDCEDTの辞書"""
        large_edt = [100] + list(range(100))
        src = {0x9f: PDCEDT(large_edt)}
        dst = deepcopy_dict_pdcedt(src)

        assert 0x9f in dst
        assert dst[0x9f] == src[0x9f]
        assert dst[0x9f] is not src[0x9f]
        assert len(dst[0x9f].edt) == 100

    def test_deepcopy_dict_many_entries(self):
        """多数のエントリを持つ辞書"""
        src = {}
        for i in range(0x80, 0x90):
            src[i] = PDCEDT([1, i])

        dst = deepcopy_dict_pdcedt(src)

        assert len(dst) == 16
        for i in range(0x80, 0x90):
            assert i in dst
            assert dst[i] == src[i]
            assert dst[i] is not src[i]

    def test_deepcopy_dict_modify_nested_edt(self):
        """ネストされたEDTの変更が独立していることを確認"""
        src = {0x80: PDCEDT([3, 0x01, 0x02, 0x03])}
        dst = deepcopy_dict_pdcedt(src)

        # コピー元のEDTを変更
        src[0x80].edt[0] = 0xFF

        # コピー先は変更されていない
        assert dst[0x80].edt[0] == 0x01
        assert src[0x80].edt[0] == 0xFF


class TestEdgeCases:
    """エッジケースのテスト"""

    def test_deepcopy_list_with_duplicates(self):
        """重複する値を持つリスト"""
        src = [1, 1, 1, 2, 2, 3]
        dst = deepcopy_list(src)
        assert dst == [1, 1, 1, 2, 2, 3]
        assert dst is not src

    def test_deepcopy_dict_with_same_values(self):
        """同じ値を持つ複数のエントリ"""
        pdcedt = PDCEDT([1, 0x30])
        src = {
            0x80: pdcedt,
            0x81: pdcedt,
            0x82: pdcedt
        }
        dst = deepcopy_dict_pdcedt(src)

        # 全て独立したコピー
        assert dst[0x80] is not dst[0x81]
        assert dst[0x81] is not dst[0x82]
        assert dst[0x80] is not src[0x80]

    def test_deepcopy_preserves_pdcedt_properties(self):
        """PDCEDTの全プロパティが保持されることを確認"""
        src = {0x80: PDCEDT([4, 0x12, 0x34, 0x56, 0x78])}
        dst = deepcopy_dict_pdcedt(src)

        assert dst[0x80].pdc == 4
        assert dst[0x80].edt == [0x12, 0x34, 0x56, 0x78]
        assert dst[0x80].length == 5


class TestRealWorldScenarios:
    """実世界のシナリオテスト"""

    def test_property_map_copy(self):
        """プロパティマップのコピー"""
        inf_map = [0x80, 0x81, 0x82, 0x88, 0x8a, 0x9d, 0x9e, 0x9f]
        set_map = [0x80, 0x81]
        get_map = [0x80, 0x81, 0x82, 0x88, 0x8a]

        inf_copy = deepcopy_list(inf_map)
        set_copy = deepcopy_list(set_map)
        get_copy = deepcopy_list(get_map)

        assert inf_copy == inf_map
        assert set_copy == set_map
        assert get_copy == get_map

        # 独立性確認
        inf_map.append(0xb0)
        assert 0xb0 not in inf_copy

    def test_elobj_pdcedts_copy(self):
        """ELOBJのpdcedts辞書のコピー"""
        pdcedts = {
            0x80: PDCEDT([1, 0x30]),  # 電源状態
            0x81: PDCEDT([1, 0x00]),  # 設置場所
            0x88: PDCEDT([1, 0x42]),  # エラー状態
            0x9d: PDCEDT([2, 0x80, 0xd6]),  # 状変アナウンスプロパティマップ
            0x9e: PDCEDT([1, 0x80]),  # Setプロパティマップ
            0x9f: PDCEDT([8, 0x80, 0x81, 0x82, 0x83, 0x88, 0x8a, 0x9d, 0x9e])  # Getプロパティマップ
        }

        pdcedts_copy = deepcopy_dict_pdcedt(pdcedts)

        # 全てのキーが存在
        assert set(pdcedts_copy.keys()) == set(pdcedts.keys())

        # 値が等しい
        for key in pdcedts:
            assert pdcedts_copy[key] == pdcedts[key]
            assert pdcedts_copy[key] is not pdcedts[key]

        # 独立性確認
        pdcedts[0x80].setEDT([0x31])
        assert pdcedts_copy[0x80].edt == [0x30]

    def test_copy_then_modify_scenario(self):
        """コピー後に変更を加えるシナリオ"""
        original_props = {
            0x80: PDCEDT([1, 0x30]),  # Power ON
            0x81: PDCEDT([1, 0x00]),
        }

        # コピーを作成
        modified_props = deepcopy_dict_pdcedt(original_props)

        # コピーを変更
        modified_props[0x80].setEDT([0x31])  # Power OFF
        modified_props[0x82] = PDCEDT([2, 0x41, 0x42])  # 新規プロパティ追加

        # 元は変更されていない
        assert original_props[0x80].edt == [0x30]
        assert 0x82 not in original_props

        # コピーは変更されている
        assert modified_props[0x80].edt == [0x31]
        assert 0x82 in modified_props


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
