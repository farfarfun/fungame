# 依赖安装

依赖包：xgboost,notegame,tqdm,pandas,numpy

# 修改配置

文件中的_path_root是 `附件1：UWB数据集` 的绝对路径

# 代码运行

需优先运行问题一，其次再求解其他题目

```python
_path_root = '附件1：UWB数据集'
base_model = BaseModel(path_root=_path_root)
# 问题一的求解
base_model.question1()
# 问题二的求解
base_model.question2()
# 问题三的求解
base_model.question3()
# 问题四的求解
base_model.question4()
# 问题五的求解
base_model.question5()


```

# 结果数据

所有中间及结果数据保存到当前路径的data文件夹下
