import numpy as np
import pandas as pd
import xgboost as xgb
from notegame.shumo.entity import Anchor, TagInfo, masks
from notegame.shumo.load_data import load_distince_data
from notegame.shumo.solution import TagDataList
from tqdm import tqdm

global_data = []
global_label = 1


class BaseModel:
    def __init__(self, path_root, tag_loc=None):
        self.tag_loc = tag_loc or np.random.random([500, 3])
        self.tag_loc[:, 0] = 2500
        self.tag_loc[:, 1] = 2500
        self.tag_loc[:, 2] = 1500
        self.path_root = path_root
        self.anchor = Anchor.new_instance1()
        self.tag_info = TagInfo(path=f'{path_root}/Tag坐标信息.txt')
        self.tag_info.cul_distance()

        self.question4_model_path = 'data/model/question4-1.model'

    def method2(self, loc, d1, near_loc):
        """
        :param near_loc:
        :param loc: tag 坐标
        :param d1: tag到锚点的目标距离
        :return:
        """
        # tag到锚点的向量
        vec = np.concatenate([self.anchor.loc, near_loc]) - loc
        # tag到锚点的计算距离
        d2 = np.linalg.norm(vec, axis=1)
        # 距离差
        ds = (d2 - d1)
        # 根据距离差算的各个锚点的差
        weight = np.reshape(ds / np.sum(np.abs(ds)), [1, 4 + near_loc.shape[0]])
        weight[-1] += 0.1
        return weight, vec, ds, d2

    def method2_steps(self, values, near_loc, learn_rate=0.05, steps=100):
        loc = np.array([2500., 2500., 1500.])
        for i in range(steps):
            for line in values:
                d1 = np.array([*line[1:5], *[0] * len(near_loc)]) + 50
                weight, vec, ds, d2 = self.method2(loc, d1, near_loc)
                # loc += learn_rate * 0.85 ** i * np.reshape(np.matmul(weight, vec), [3])
                loc += learn_rate * (steps - i) / steps * np.reshape(np.matmul(weight, vec), [3])
        return loc

    def method1(self, loc, d1, mask=None):
        """
        :param loc: tag 坐标
        :param d1: tag到锚点的目标距离
        :param mask:屏蔽标记
        :return:
        """
        mask = mask if mask is not None else np.array([1., 1, 1, 1])
        # tag到锚点的向量
        vec = self.anchor.loc - loc
        # tag到锚点的计算距离
        d2 = np.linalg.norm(vec, axis=1)
        # 距离差
        ds = (d2 - d1) * mask

        # 根据距离差算的各个锚点的差
        weight = np.reshape(ds / np.sum(np.abs(ds)), [1, 4])
        return weight, vec, ds, d2

    def method1_steps(self, values, learn_rate=0.05, steps=100, mask=None):
        loc = np.array([2500., 2500., 1500.])
        for i in range(steps):
            for line in values:
                d1 = line[1:5] + 50
                weight, vec, ds, d2 = self.method1(loc, d1, mask=mask)
                # loc += learn_rate * 0.85 ** i * np.reshape(np.matmul(weight, vec), [3])
                loc += learn_rate * (steps - i) / steps * np.reshape(np.matmul(weight, vec), [3])
        return loc

    def question3_train1(self, train_data, tag_list=None):
        """
        data公式 [[tag_id,d0,d1,d2,d3]]
        """
        tag_list = tag_list if tag_list is not None else np.arange(1, 10)

        for tag_id in tag_list:
            value = train_data[train_data['tag_id'] == tag_id].values
            self.tag_info.tag_df.loc[self.tag_info.tag_df['tag_id'] == tag_id, 'size'] = len(value)

            self.tag_loc[tag_id] = self.method1_steps(value)
            self.question2_verify(tag_id)

    def check_normal(self, value, label=False):
        max_i, max_v, max_s1, max_s3, max_loc = -1, 0, 0, 10000, None
        _level = 500
        for i in range(4):
            loc = self.method1_steps([value], mask=masks[i])
            # global_data.append([value[0], i, *loc, *value[1:5], global_label])
            # print([value[0], i, *loc])
            l = np.linalg.norm(loc - self.anchor.loc, axis=1) - value[1:]

            s1 = -l[i]
            s2 = (sum(l) - l[i]) / 3.
            s3 = np.sqrt((sum((l - s2) ** 2) - (l[i] - s2) ** 2) / 3)

            if (abs(s1) > 100) and s3 < max_s3:
                max_i = i
                max_s1, max_s3, max_loc = abs(s1), s3, loc
            # print(s1, s2, s3)
        if max_s1 > 450:
            _level = 500
        elif max_s1 > 350:
            _level = 400
        elif max_s1 > 300:
            _level = 300
        elif max_s1 > 200:
            _level = 200
        elif max_s1 > 100:
            _level = 100

        return max_i, max_loc, _level

    def question1_train2(self, train_data, tag_list=None, label='normal'):
        """
        data公式 [[tag_id,d0,d1,d2,d3]]
        """
        tag_list = tag_list if tag_list is not None else np.arange(1, 10)

        for tag_id in tag_list:
            values = train_data[train_data['tag_id'] == tag_id].values
            self.tag_info.tag_df.loc[self.tag_info.tag_df['tag_id'] == tag_id, 'size'] = len(values)

            if label == 'abnormal':  # or label == 'normal':
                for i, value in enumerate(values):
                    _label, _loc, _level = self.check_normal(value)
                    if _label >= 0:
                        # print(tag_id, _label, value)
                        values[i][_label + 1] -= _level
                        # print(tag_id, _label, value)

            self.tag_loc[tag_id] = self.method1_steps(values)
            self.question2_verify(tag_id)

    def question2_verify(self, tag_id):
        s1 = np.round(self.tag_loc[tag_id], 0)
        s2 = self.tag_info.tag_df[self.tag_info.tag_df['tag_id'] == tag_id][['x', 'y', 'z']].values[0]

        e1 = np.linalg.norm(s1 - s2)
        self.tag_info.tag_df.loc[self.tag_info.tag_df['tag_id'] == tag_id, 'err'] = e1
        size = self.tag_info.tag_df.loc[self.tag_info.tag_df["tag_id"] == tag_id, "size"].values[0]

        print(f'{tag_id}\t{e1}\t{s1}\t{s2}\t{size}')

    def question2_step1(self):
        def cul_and_save(label='normal'):
            train_data = pd.read_csv(f'data/train_{label}.csv')

            self.tag_info.tag_df['err'] = 50000
            self.tag_info.tag_df['size'] = 50000
            tag_list = np.arange(1, 325)
            self.question1_train2(train_data, tag_list=tag_list, label=label)
            self.tag_info.tag_df['err2'] = self.tag_info.tag_df['err'] * self.tag_info.tag_df['err']

            print(self.tag_info.tag_df['err'].mean(), np.sqrt(self.tag_info.tag_df['err2'].mean()))
            tmp = pd.DataFrame(self.tag_loc).reset_index()
            tmp.columns = ['id', 'x', 'y', 'z']
            tmp = tmp[(tmp['id'] >= 1) & (tmp['id'] <= 324)]
            tmp.to_csv(f'data/result/question2-{label}.csv', index=False)

        cul_and_save('normal')
        cul_and_save('abnormal')

    def predict_data(self, path):
        dis = load_distince_data(path)
        res = []
        for i, line in enumerate(dis[['tag_id', 'dis_0', 'dis_1', 'dis_2', 'dis_3']].values):

            _label, _loc, _level = self.check_normal(line, label=True if i >= 5 else False)

            if _label >= 0 and i >= 5:
                line[_label + 1] -= _level

            loc = self.method1_steps([line])
            res.append(loc)
            print(line, _label, loc)
        res = pd.DataFrame(res)
        res = np.round(res)
        res.columns = ['x', 'y', 'z']
        return res

    def question4_step1(self):
        def train(data):
            res = []
            for tag_id in tqdm(tag_list):
                for value in data[data['tag_id'] == tag_id].values:
                    loc = self.method1_steps([value])
                    weight, vec, ds, d2 = self.method1(loc, value[1:5])
                    res.append([tag_id, *loc, *ds, *d2, *value[1:5]])
            res = pd.DataFrame(res)
            res.columns = ['tag_id', 'x', 'y', 'z',
                           'ds0', 'ds1', 'ds2', 'ds3',
                           'dis0', 'dis1', 'dis2', 'dis3',
                           'tar0', 'tar1', 'tar2', 'tar3']
            return res

        tag_list = np.arange(1, 325)
        train1 = train(pd.read_csv(f'data/train_normal.csv'))
        train2 = train(pd.read_csv(f'data/train_abnormal.csv'))
        train1['label'] = 1
        train2['label'] = 0
        train3 = pd.concat([train1, train2])
        train3.to_csv('data/result/question4-step1.csv', index=False)

    def question4_step2(self):
        df = pd.read_csv('data/result/question4-step1.csv')

        df['tag_id'] = df['tag_id'].astype('int')
        df['mean'] = np.mean(df[['ds0', 'ds1', 'ds2', 'ds3']], axis=1)

        for i in range(4):
            df[f'ps{i}'] = df[f'ds{i}'] / df['mean'] / 4
        df = df.sample(len(df)).reset_index()
        size = round(len(df) * 0.8)

        train_cols = [*[f'ds{i}' for i in range(4)], *[f'ps{i}' for i in range(4)], 'x', 'y', 'z', 'mean']

        label_cols = 'label'

        dtrain = xgb.DMatrix(df.loc[:size, train_cols].values, label=df.loc[:size, label_cols].values)
        dtest = xgb.DMatrix(df.loc[size:, train_cols].values)

        param = {'max_depth': 4,
                 'eta': 0.1,
                 'objective': 'multi:softmax',
                 'num_class': 2,
                 'eval_metric': 'mlogloss'}
        num_round = 2
        bst = xgb.train(param, dtrain, num_round)
        bst.save_model(self.question4_model_path)
        pred = bst.predict(dtest)

        t = pd.DataFrame(np.transpose([df.loc[size:, label_cols].values, pred]))
        t.columns = ['true', 'pred']
        t['num'] = 1
        t1 = t.groupby(['true', 'pred'])['num'].count().reset_index()

        print(f'total:{len(df)},positive size:{len(df[df["label"] == 1])}\tnegative size:{len(df[df["label"] == 0])}')
        print(f'train size:{size}\ttest size:{len(df) - size}')
        print("混淆矩阵为")
        print(t1)
        print(f"准确率为{t1[t1['true'] == t1['pred']]['num'].sum() / t1['num'].sum()}")

    def question4_step3(self):
        bst = xgb.Booster(model_file=self.question4_model_path)
        values = load_distince_data('data/prepare/data4.txt')
        res = []
        for value in values[['tag_id', 'dis_0', 'dis_1', 'dis_2', 'dis_3']].values:
            loc = self.method1_steps([value])
            weight, vec, ds, d2 = self.method1(loc, value[1:5])
            res.append([0, *loc, *ds, *d2, *value[1:5]])
        df = pd.DataFrame(res)
        df.columns = ['tag_id', 'x', 'y', 'z',
                      'ds0', 'ds1', 'ds2', 'ds3',
                      'dis0', 'dis1', 'dis2', 'dis3',
                      'tar0', 'tar1', 'tar2', 'tar3']

        df['mean'] = np.mean(df[['ds0', 'ds1', 'ds2', 'ds3']], axis=1)
        for i in range(4):
            df[f'ps{i}'] = df[f'ds{i}'] / df['mean'] / 4

        train_cols = [*[f'ds{i}' for i in range(4)], *[f'ps{i}' for i in range(4)], 'x', 'y', 'z', 'mean']
        matrix = xgb.DMatrix(df[train_cols].values)
        pred = bst.predict(matrix)
        print(pred)

    def question5_step1(self):
        def train(data):
            res = []
            last_loc = np.zeros([1, 3], dtype='float')
            for i, value in enumerate(data):
                _label, _loc, _level = self.check_normal(value)
                if _label >= 0:
                    # print(tag_id, _label, value)
                    # value[_label + 1] -= _level
                    pass
                print(i, _label, value, _level)
                loc = self.method2_steps([value], near_loc=last_loc)
                tar = [*value[1:5], 0]
                weight, vec, ds, d2 = self.method2(loc, tar, near_loc=last_loc)
                res.append([0, *loc[:3], *ds[:4], *d2[:4], *value[1:5]])
                last_loc = np.array([loc])

            res = pd.DataFrame(res)
            res.columns = ['tag_id', 'x', 'y', 'z',
                           'ds0', 'ds1', 'ds2', 'ds3',
                           'dis0', 'dis1', 'dis2', 'dis3',
                           'tar0', 'tar1', 'tar2', 'tar3']
            return res

        df = train(load_distince_data(f'data/prepare/data5.txt')[['tag_id', 'dis_0', 'dis_1', 'dis_2', 'dis_3']].values)
        for key in ['x', 'y', 'z']:
            # df[key] = df[key].rolling(window=5, min_periods=1).mean()
            pass
        df[['x', 'y', 'z']].to_csv('data/result/question5-track.csv', index=False)
        s = [f'[{line[0]},{line[1]},{line[2]}]' for line in df[['x', 'y', 'z']].values]
        print(','.join(s))

    def question1(self):
        TagDataList(self.path_root).run()

    def question2(self):
        self.question2_step1()
        res = self.predict_data('data/prepare/data2.txt')
        res.to_csv('data/result/question2-predict.csv')
        print('done')

    def question3(self):
        self.anchor = Anchor.new_instance2()
        res = self.predict_data('data/prepare/data3.txt')
        res.to_csv('data/result/question3-predict.csv')
        print('done')

    def question4(self):
        # self.question4_step1()
        # self.question4_step2()
        self.question4_step3()

    def question5(self):
        self.question5_step1()
