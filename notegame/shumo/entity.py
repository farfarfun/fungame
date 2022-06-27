import itertools
import json

import numpy as np
from notegame.shumo.load_data import load_tag_info

masks = np.array([[0, 1, 1, 1],
                  [1, 0, 1, 1],
                  [1, 1, 0, 1],
                  [1, 1, 1, 0]])


class Anchor:
    def __init__(self, loc):
        self.loc = loc
        self.distance = None

    def init(self):
        self.distance = np.zeros([self.loc.shape[0], self.loc.shape[0]])
        for i in range(self.loc.shape[0]):
            for j in range(self.loc.shape[0]):
                self.distance[i][j] = round(np.linalg.norm(self.loc[i] - self.loc[j]), 5)

    @staticmethod
    def new_instance1():
        loc = np.array([[0, 0, 1300], [5000, 0, 1700],
                        [0, 5000, 1700], [5000, 5000, 1300]])
        anchor = Anchor(loc=loc)
        anchor.init()
        return anchor

    @staticmethod
    def new_instance2():
        loc = np.array([[0, 0, 1200], [5000, 0, 1600],
                        [0, 3000, 1600], [5000, 3000, 1200]])
        anchor = Anchor(loc=loc)
        anchor.init()
        return anchor


class TagInfoBak1:
    def __init__(self, path, anchor=None):
        self.tag_df = None
        self.anchor = anchor or Anchor.new_instance1()
        self.init(path)

    def init(self, path):
        self.tag_df = load_tag_info(path)

    def cul_distance(self):
        a = np.array(self.tag_df[['x', 'y', 'z']].values)
        for i in range(4):
            b = a - self.anchor.loc[i]
            self.tag_df[f'd{i}'] = np.round(np.linalg.norm(b, axis=1))


class TagInfo:
    def __init__(self, path, anchor=None):
        self.tag_df = None
        self.anchor = anchor or Anchor.new_instance1()
        self.init(path)

    def init(self, path):
        self.tag_df = load_tag_info(path)

    def cul_distance(self):
        a = np.array(self.tag_df[['x', 'y', 'z']].values)
        for i in range(4):
            b = a - self.anchor.loc[i]
            self.tag_df[f'd{i}'] = np.round(np.linalg.norm(b, axis=1))

    def check_data(self, tag_id, df0, normal=True):
        def check_field(df, field):
            value = df[field].values
            vmin = np.percentile(value, 20)
            vmax = np.percentile(value, 80)
            df2 = df[(df['dis_0'] >= vmin) & (df['dis_0'] <= vmax)]
            vmean = np.mean(df2['dis_0'])
            df.loc[(df['dis_0'] <= vmean - 20) | (df['dis_0'] >= vmean + 20), 'normal'] = 2

        def check(df):
            d1 = df[['normal', 'data_index', *[f'dis_{i}' for i in range(4)]]]

            # 异常值检测
            for index, line in enumerate(json.loads(d1.to_json(orient='records'))):
                is_normal = True
                if line['normal'] > 0:
                    continue
                # 看某条记录是佛有异常数据
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
