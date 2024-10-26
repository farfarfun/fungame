import json

import numpy as np
import pandas as pd
from notegame.shumo.entity import Anchor, TagInfo
from notegame.shumo.load_data import load_all_and_merge
from tqdm import tqdm


class TagDataList:
    def __init__(self, path_root):
        self.anchor = Anchor.new_instance1()
        self.tag_info = TagInfo(f'{path_root}/Tag坐标信息.txt')
        self.df_normal = load_all_and_merge(f'{path_root}/正常数据')
        self.df_abnormal = load_all_and_merge(f'{path_root}/异常数据')
        print(len(self.df_normal))

    def check(self, df=None, normal=True):
        if df is None:
            df = self.df_normal
        df_duplicates = df.groupby(['tag_id', *[f'dis_{i}' for i in range(4)]]).max(
            'data_index').reset_index()[['tag_id', 'data_index']]
        df_duplicates['normal'] = 0
        df2 = pd.merge(df, df_duplicates, on=['tag_id', 'data_index'], how='left')
        df2.fillna(1, inplace=True)
        assert len(df) == len(df2)
        df = df2
        dfs = []
        for tag_info in tqdm(json.loads(self.tag_info.tag_df.to_json(orient='records'))):
            tag_id = tag_info['tag_id']
            tag_df = self.tag_info.check_data(tag_id, df[df['tag_id'] == tag_id], normal=normal)
            dfs.append(tag_df)
            s0 = len(tag_df[tag_df['normal'] == 0])
            s1 = len(tag_df[tag_df['normal'] == 1])
            s2 = len(tag_df[tag_df['normal'] == 2])
            # print(f'{tag_id}\t{s2}->{s1}->{s0}')

        return pd.concat(dfs)

    def analyse(self):
        df1 = pd.merge(self.df_normal, self.tag_info.tag_df, on='tag_id', how='left')
        df2 = df1[[*[f'dis_{i}' for i in range(4)], *[f'd{i}' for i in range(4)]]]
        df3 = df1[[f'dis_{i}' for i in range(4)]].values - df1[[f'd{i}' for i in range(4)]].values
        df31 = pd.DataFrame(df3)
        df31.columns = [f'e{i}' for i in range(4)]
        df2 = pd.concat([df2, df31], axis=1)

        df4 = np.linalg.norm(df3, axis=1)
        df4.sort()

        print(df2.head(5))

        print(df4)

        df3.resize([1, 4 * len(df1)])
        df3 = df3[0]
        df3.sort()
        print(df3)

    def save_train_data(self, df0, normal=True):
        tag = 'normal' if normal else 'abnormal'
        df0 = pd.merge(df0, self.tag_info.tag_df, on='tag_id', how='left')
        df1 = df0[df0['normal'] == 0][['tag_id', 'dis_0', 'dis_1', 'dis_2', 'dis_3']]
        df1 = df1.sample(len(df1)).reset_index(drop=True)
        df0.to_csv(f'data/all_{tag}.csv', index=None)
        df1.to_csv(f'data/train_{tag}.csv', index=None)

    def run(self):
        self.tag_info.cul_distance()
        self.df_normal = self.check(self.df_normal)
        self.df_abnormal = self.check(self.df_abnormal, normal=False)
        # self.analyse()
        self.save_train_data(self.df_normal)
        self.save_train_data(self.df_abnormal, normal=False)
