"""UWB 定位数学建模竞赛用到的实体模型：锚点（Anchor）与标签（Tag）。

四个锚点固定安装在房间四角，标签在房间内移动并上报到每个锚点的测距值。
本模块属一次性竞赛代码，坐标与阈值都是针对那次比赛的场地写死的。
"""

import itertools
import json

import numpy as np
import pandas as pd

from fungame.shumo.load_data import load_tag_info

masks = np.array([[0, 1, 1, 1],
                  [1, 0, 1, 1],
                  [1, 1, 0, 1],
                  [1, 1, 1, 0]])


class Anchor:
    """四个 UWB 锚点的位置模型，附带锚点两两之间的真实距离矩阵。"""

    def __init__(self, loc: np.ndarray):
        """
        Args:
            loc: 形状 ``(n, 3)`` 的锚点坐标数组，每行是一个锚点的 ``(x, y, z)``。
        """
        self.loc = loc
        self.distance: np.ndarray | None = None

    def init(self) -> None:
        """按欧氏距离计算锚点两两之间的距离矩阵，结果写入 ``self.distance``。

        距离矩阵形状为 ``(n, n)``，对角线为 0，保留 5 位小数。
        """
        self.distance = np.zeros([self.loc.shape[0], self.loc.shape[0]])
        for i in range(self.loc.shape[0]):
            for j in range(self.loc.shape[0]):
                self.distance[i][j] = round(np.linalg.norm(self.loc[i] - self.loc[j]), 5)

    @staticmethod
    def new_instance1() -> "Anchor":
        """构造第一组场地的锚点布局（5000x5000 房间），并预先算好距离矩阵。"""
        loc = np.array([[0, 0, 1300], [5000, 0, 1700],
                        [0, 5000, 1700], [5000, 5000, 1300]])
        anchor = Anchor(loc=loc)
        anchor.init()
        return anchor

    @staticmethod
    def new_instance2() -> "Anchor":
        """构造第二组场地的锚点布局（5000x3000 房间），并预先算好距离矩阵。"""
        loc = np.array([[0, 0, 1200], [5000, 0, 1600],
                        [0, 3000, 1600], [5000, 3000, 1200]])
        anchor = Anchor(loc=loc)
        anchor.init()
        return anchor


class TagInfo:
    """标签真实坐标表，并在其上做「标签到各锚点的真实距离」与异常值标注。"""

    def __init__(self, path: str, anchor: Anchor | None = None):
        """
        Args:
            path: `Tag坐标信息.txt` 的路径，交给
                :func:`~fungame.shumo.load_data.load_tag_info` 解析。
            anchor: 锚点布局。为 ``None`` 时使用 :meth:`Anchor.new_instance1`。
        """
        self.tag_df: pd.DataFrame | None = None
        self.anchor = anchor or Anchor.new_instance1()
        self.init(path)

    def init(self, path: str) -> None:
        """（重新）从 ``path`` 加载标签坐标表到 ``self.tag_df``。"""
        self.tag_df = load_tag_info(path)

    def cul_distance(self) -> None:
        """为 ``self.tag_df`` 补上 ``d0``~``d3`` 四列：标签到各锚点的真实距离（四舍五入取整）。"""
        a = np.array(self.tag_df[['x', 'y', 'z']].values)
        for i in range(4):
            b = a - self.anchor.loc[i]
            self.tag_df[f'd{i}'] = np.round(np.linalg.norm(b, axis=1))

    def check_data(self, tag_id: int, df0: pd.DataFrame, normal: bool = True) -> pd.DataFrame:
        """在距离观测宽表上标注异常采样，返回带标注的副本（不修改入参）。

        Args:
            tag_id: 当前标签编号。仅用于调用方串联日志/分组，函数内部不参与计算。
            df0: 距离观测宽表，至少含 ``normal``、``data_index`` 与
                ``dis_0``~``dis_3`` 列，``normal`` 为 0 表示尚未判定。
            normal: 是否执行逐列的分位数离群检测。``False`` 时只跑三角不等式检查。

        Returns:
            ``df0`` 的副本。``normal`` 列被标成 2 表示该采样在某个 ``dis_i``
            上离群；标成 3 表示违反三角不等式——但见下面的实现说明，这一档
            当前不会被触发。
        """

        def check_field(df, field):
            # 原实现取 df[field] 算分位数，后续却一律写死 'dis_0'，等于把 dis_1..dis_3
            # 的检查重复做了三遍 dis_0；这里统一改为按传入的 field 判断
            value = df[field].values
            vmin = np.percentile(value, 20)
            vmax = np.percentile(value, 80)
            df2 = df[(df[field] >= vmin) & (df[field] <= vmax)]
            vmean = np.mean(df2[field])
            df.loc[(df[field] <= vmean - 20) | (df[field] >= vmean + 20), 'normal'] = 2

        def check(df):
            d1 = df[['normal', 'data_index', *[f'dis_{i}' for i in range(4)]]]

            # 异常值检测
            for index, line in enumerate(json.loads(d1.to_json(orient='records'))):
                is_normal = True
                if line['normal'] > 0:
                    continue
                # 看某条记录是否有异常数据
                # 注意：下面的三角不等式判断在当初比赛时被手工关掉了（`is_normal = False`
                # 与调试 print 都被注释掉），因此 normal=3 这一档实际永远不会被标记。
                # 这里保持原有行为不变，只是把这个事实写清楚，避免被误读成仍在生效。
                for i, j in itertools.combinations(np.arange(4), 2):
                    a, b, c = line[f'dis_{i}'], line[f'dis_{j}'], self.anchor.distance[i][j]

                    # 如果不满足三角形任意两边的和大于第三边
                    alpha = 0.95
                    beta = 0
                    if a * alpha - beta > b + c or b * alpha - beta > a + c or c * alpha - beta > a + b:
                        # print(i, j, a, b, c)
                        # is_normal = False
                        break

                if not is_normal:
                    df.loc[index, 'normal'] = 3

        df0 = df0.copy()

        if normal:
            for field in [f'dis_{i}' for i in range(4)]:
                check_field(df0, field)
        check(df0)
        return df0
