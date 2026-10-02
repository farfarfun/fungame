"""shumo 模块的正常/边界/失败路径测试，覆盖数据加载、路径配置与公开求解流程。

`shumo.model` 依赖 `xgboost`（可选 extra，未默认安装），这里只测试不依赖
`xgboost` 的 `load_data` / `entity` / `solution`，避免给测试环境引入重依赖。
"""

import os

import numpy as np
import pytest

from fungame.shumo.entity import Anchor, TagInfo
from fungame.shumo.load_data import (
    load_all_and_merge,
    load_distince_data,
    load_distince_data_origin,
    load_tag_info,
)
from fungame.shumo.solution import TagDataList


def _write(path, content):
    with open(path, "w") as f:
        f.write(content)


# ---------- load_tag_info：锚点/标签坐标文本解析 ----------


def test_load_tag_info_parses_normal_rows(tmp_path):
    """正常路径：两行表头后紧跟若干 `tag_id x y z` 记录，坐标单位按 *10 换算。"""
    content = (
        "header line 1\n"
        "header line 2\n"
        "1:  100.5   200.5    300.5 \n"
        "2: 400.25 500.25 600.25\n"
    )
    path = tmp_path / "tag.txt"
    _write(path, content)

    df = load_tag_info(str(path))

    assert df["tag_id"].tolist() == [1, 2]
    assert df["x"].tolist() == pytest.approx([1005.0, 4002.5])
    assert df["y"].tolist() == pytest.approx([2005.0, 5002.5])
    assert df["z"].tolist() == pytest.approx([3005.0, 6002.5])


def test_load_tag_info_ignores_trailing_blank_lines(tmp_path):
    """边界用例：数据区末尾的空行不应被当成一条记录解析（不含空格会被过滤）。"""
    content = "header line 1\nheader line 2\n1: 0 0 130\n\n"
    path = tmp_path / "tag_trailing_blank.txt"
    _write(path, content)

    df = load_tag_info(str(path))

    assert df["tag_id"].tolist() == [1]


# ---------- load_distince_data_origin / load_distince_data：距离观测数据解析 ----------


def _make_distance_file(tmp_path, name="1.txt"):
    lines = []
    for data_index in (1, 2):
        for anchor_id in (0, 1, 2, 3):
            dist = 100.0 * anchor_id + data_index
            lines.append(f"c1:1700000000:c3:5:{anchor_id}:{dist}:{dist + 0.5}:c8:{data_index}")
    # 字段数不对的脏行，解析时应被过滤掉，不应导致整体解析失败
    lines.append("broken:line:with:wrong:field:count")
    path = tmp_path / name
    _write(path, "\n".join(lines) + "\n")
    return path


def test_load_distince_data_origin_filters_malformed_lines(tmp_path):
    """失败/边界路径：字段数不满足 9 个的脏行应被丢弃，不抛异常也不混入结果。"""
    path = _make_distance_file(tmp_path)

    df = load_distince_data_origin(str(path))

    assert len(df) == 8  # 2 个 data_index * 4 个 anchor，脏行被过滤
    assert set(df["anchor_id"]) == {"0", "1", "2", "3"}


def test_load_distince_data_pivots_each_anchor_to_a_column(tmp_path):
    """正常路径：按 anchor_id 把长表透视成 dis_0..dis_3 宽表，每个 data_index 一行。"""
    path = _make_distance_file(tmp_path)

    df = load_distince_data(str(path))

    assert len(df) == 2
    assert df["data_index"].tolist() == ["1", "2"]
    assert df["dis_0"].tolist() == pytest.approx([1.0, 2.0])
    assert df["dis_3"].tolist() == pytest.approx([301.0, 302.0])


# ---------- load_all_and_merge：路径配置、缓存与目录批量合并 ----------


def test_load_all_and_merge_builds_from_directory_and_writes_cache(tmp_path):
    """正常路径：遍历目录下按 tag_id 命名的文件，合并后写入指定的 target_file。"""
    path_dir = tmp_path / "正常数据"
    path_dir.mkdir()
    _make_distance_file(tmp_path, name="正常数据/7.txt")
    target_file = tmp_path / "merged.csv"

    res = load_all_and_merge(str(path_dir), target_file=str(target_file), overwrite=True)

    assert os.path.exists(target_file)
    assert (res["tag_id"] == 7).all()
    assert len(res) == 2


def test_load_all_and_merge_uses_cache_without_touching_path_dir(tmp_path):
    """边界用例：target_file 已存在且 overwrite=False 时直接读缓存，
    即使 path_dir 根本不存在也不应报错（验证路径配置的缓存短路逻辑）。"""
    path_dir = tmp_path / "正常数据"
    path_dir.mkdir()
    _make_distance_file(tmp_path, name="正常数据/7.txt")
    target_file = tmp_path / "merged.csv"
    load_all_and_merge(str(path_dir), target_file=str(target_file), overwrite=True)

    res = load_all_and_merge("/path/does/not/exist", target_file=str(target_file), overwrite=False)

    assert len(res) == 2


# ---------- Anchor / TagInfo：公开流程里用到的锚点与标签模型 ----------


def test_anchor_new_instance1_distance_matrix_is_symmetric_and_zero_diagonal():
    anchor = Anchor.new_instance1()

    assert anchor.distance.shape == (4, 4)
    assert np.allclose(np.diag(anchor.distance), 0)
    assert np.allclose(anchor.distance, anchor.distance.T)
    assert anchor.distance[0][1] == pytest.approx(np.linalg.norm(anchor.loc[0] - anchor.loc[1]))


def test_taginfo_cul_distance_adds_distance_columns(tmp_path):
    """公开流程：TagInfo 从文件加载坐标后，cul_distance 应补全到各锚点的距离列。

    `load_tag_info` 会把坐标值乘以 10（详见其实现），这里写入 `130` 使换算后的
    z 坐标 `1300` 与 `Anchor.new_instance1()` 的锚点 0 坐标 `[0, 0, 1300]` 对齐。
    """
    content = "h1\nh2\n1: 0 0 130\n"
    path = tmp_path / "tag.txt"
    _write(path, content)

    tag_info = TagInfo(str(path))
    tag_info.cul_distance()

    assert tag_info.tag_df.loc[0, "d0"] == pytest.approx(0.0)
    assert {"d0", "d1", "d2", "d3"}.issubset(tag_info.tag_df.columns)


# ---------- TagDataList：公开求解入口的最小可运行路径 ----------


def test_tag_data_list_run_builds_train_csv_from_fixture_dirs(tmp_path, monkeypatch):
    """公开流程边界用例：TagDataList() 构造时会加载坐标信息与正常/异常数据目录，
    用最小 fixture 验证整条链路可以跑通（不依赖真实竞赛数据集）。"""
    monkeypatch.chdir(tmp_path)
    # load_all_and_merge 默认把缓存写到相对路径 data/<dirname>.csv，需要先建好目录
    (tmp_path / "data").mkdir()

    tag_path = tmp_path / "Tag坐标信息.txt"
    _write(tag_path, "h1\nh2\n5: 0 0 130\n")

    normal_dir = tmp_path / "正常数据"
    normal_dir.mkdir()
    _make_distance_file(tmp_path, name="正常数据/5.txt")

    abnormal_dir = tmp_path / "异常数据"
    abnormal_dir.mkdir()
    _make_distance_file(tmp_path, name="异常数据/5.txt")

    tag_list = TagDataList(path_root=str(tmp_path))

    assert len(tag_list.df_normal) == 2
    assert len(tag_list.df_abnormal) == 2
