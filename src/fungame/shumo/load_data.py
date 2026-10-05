"""UWB 定位数学建模竞赛数据集的读取与整形工具。

数据集由两类文本文件组成：

- `Tag坐标信息.txt`：两行表头 + 每行 ``tag_id: x y z``，坐标单位为厘米；
- `正常数据/` 与 `异常数据/` 目录下按 ``<tag_id>.txt`` 命名的距离观测文件，
  每行是 9 个冒号分隔字段的原始上报记录。

本模块属一次性竞赛代码，字段名与清洗规则均依赖该数据集的具体格式。
"""

import os

import pandas as pd
from tqdm import tqdm


def load_tag_info(path: str) -> pd.DataFrame:
    """读取标签（Tag）真实坐标文件。

    Args:
        path: `Tag坐标信息.txt` 的路径。文件前两行是表头，之后每行形如
            ``1: 100.5 200.5 300.5``；连续空格与行尾空格都会被归一化。

    Returns:
        含 ``tag_id``（int）与 ``x`` / ``y`` / ``z``（float）四列的 DataFrame。
        坐标值已统一乘以 10，换算成与距离观测一致的单位。
    """
    with open(path, encoding='utf-8') as file:
        tag_info = file.read()
    tag_info = tag_info.replace('  ', ' ')
    tag_info = tag_info.replace('  ', ' ')
    tag_info = tag_info.replace('  ', ' ')
    tag_info = tag_info.replace(':', '')
    tag_info = tag_info.replace(' \n', '\n')
    tag_info_list = tag_info.split('\n')

    tmp = [line.split(' ') for line in tag_info_list[2:] if ' ' in line]

    tag_df = pd.DataFrame(tmp)

    tag_df.columns = ['tag_id', 'x', 'y', 'z']
    tag_df['tag_id'] = tag_df['tag_id'].astype('int')
    for key in ['x', 'y', 'z']:
        tag_df[key] = tag_df[key].astype('float')*10.0
    return tag_df


def load_distince_data_origin(path: str) -> pd.DataFrame:
    """读取单个标签的原始距离观测文件（长表，不做透视）。

    Args:
        path: 距离观测文件路径，文件名形如 ``<tag_id>.txt``。

    Returns:
        长表 DataFrame，一行是「某次采样对某个锚点」的一条观测，列为
        ``c1`` / ``unixtime`` / ``c3`` / ``tag_id`` / ``anchor_id`` /
        ``distance`` / ``distance_check`` / ``c8`` / ``data_index``。
        字段数不等于 9 的脏行会被直接丢弃；``c1`` / ``c3`` / ``c8`` 是
        数据集里未使用的原始字段，保持字符串原样。
    """
    with open(path, encoding='utf-8') as file:
        d1 = file.read()
    d2 = d1.split('\n')
    d3 = pd.DataFrame([line.split(':') for line in d2 if len(line.split(':')) == 9])
    d3.columns = ['c1', 'unixtime', 'c3', 'tag_id', 'anchor_id', 'distance', 'distance_check', 'c8', 'data_index']
    d3['tag_id'] = d3['tag_id'].astype('float')
    d3['distance'] = d3['distance'].astype('float')
    d3['distance_check'] = d3['distance_check'].astype('float')

    return d3


def load_distince_data(path: str) -> pd.DataFrame:
    """读取单个标签的距离观测文件，并按锚点透视成宽表。

    Args:
        path: 距离观测文件路径，文件名形如 ``<tag_id>.txt``。

    Returns:
        宽表 DataFrame，一行对应一次采样（``data_index``），含四个锚点的
        实测距离 ``dis_0``~``dis_3`` 与校验距离 ``dis_c_0``~``dis_c_3``。

    Raises:
        AssertionError: 两张透视表与分组结果的行数不一致，说明原始文件里
            存在缺失某个锚点的采样。
    """
    d3 = load_distince_data_origin(path)

    d41 = d3[['data_index', 'anchor_id', 'distance']].pivot(index='data_index', columns='anchor_id', values='distance')
    d41.reset_index(inplace=True)
    d41.columns = ['data_index', 'dis_0', 'dis_1', 'dis_2', 'dis_3']

    d42 = d3[['data_index', 'anchor_id', 'distance_check']].pivot(
        index='data_index', columns='anchor_id', values='distance_check')
    d42.reset_index(inplace=True)
    d42.columns = ['data_index', 'dis_c_0', 'dis_c_1', 'dis_c_2', 'dis_c_3']

    d5 = d3[['c1', 'data_index', 'c3', 'tag_id', 'c8', 'unixtime']].groupby(['data_index']).max().reset_index()

    d6 = pd.merge(d5, d41, on=['data_index'])
    d6 = pd.merge(d6, d42, on=['data_index'])

    d6.reset_index(drop=True, inplace=True)

    # 原写法是 len(d41) == len(d41)，把 d42 漏写成了 d41，distance_check 透视表
    # 的行数对不上时这条断言根本不会触发
    assert len(d41) == len(d42) == len(d5) == len(d6)

    return d6


def load_all_and_merge(
    path_dir: str, target_file: str | None = None, overwrite: bool = False
) -> pd.DataFrame:
    """批量读取一个目录下所有标签的距离观测文件并合并，结果带 CSV 缓存。

    Args:
        path_dir: 存放 ``<tag_id>.txt`` 的目录，例如 `正常数据/` 或 `异常数据/`。
        target_file: 缓存 CSV 的写出路径。默认是相对路径 ``data/<目录名>.csv``；
            所在目录不存在时会自动创建。
        overwrite: 为 ``False`` 且缓存文件已存在时直接读缓存，不再扫描
            ``path_dir``；为 ``True`` 时强制重新读取并覆盖缓存。

    Returns:
        所有标签合并后的宽表 DataFrame，额外带一列 ``tag_id``（取自文件名）。
    """
    target_file = target_file or f'data/{os.path.basename(path_dir)}.csv'

    if not overwrite and os.path.exists(target_file):
        return pd.read_csv(target_file)

    file_list = os.listdir(path_dir)
    file_list = sorted(file_list, key=lambda x: int(x.split('.')[0]))

    dfs = []
    for file_name in tqdm(file_list):
        tag_id = int(file_name.split('.')[0])
        path = os.path.join(path_dir, file_name)
        df1 = load_distince_data(path)
        df1['tag_id'] = tag_id
        dfs.append(df1)

    res = pd.concat(dfs)
    # 目标目录默认是 data/，不存在时 to_csv 会直接 FileNotFoundError
    target_dir = os.path.dirname(os.path.abspath(target_file))
    os.makedirs(target_dir, exist_ok=True)
    res.to_csv(target_file, index=False)
    return res
