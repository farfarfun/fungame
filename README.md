# fungame

这是一个游戏相关代码的杂货仓库（umbrella 仓库），把几个互不相关的小项目放在一起维护，**不是**一个统一封装的游戏 SDK。

- `src/fungame/games/` 下是实际代码：
  - `fungame.games.nonogram` —— 数织（Nonogram）自动求解器，含棋盘建模、多种求解算法（`solver/bgu.py`、`solver/simpson.py`、`solver/machine.py` 等）和 ASCII 渲染器。
  - `fungame.games.sudoku` —— 数独的生成/求解代码（`Sudoku` 类 + `sudoku_generate` / `sudoku_solve_solution` 等函数）。
  - `fungame.games.topwar` —— 针对手游《Top War》的自动化脚本（实体建模、请求/响应封装、任务/礼包码等），依赖 `funsecret` 中预先配置好的账号凭据。
  - `fungame.shumo` —— 一次数学建模比赛（UWB 定位数据分析）的解题脚本，属于一次性代码，未再维护；相关的 `xgboost` 依赖只在安装 `fungame[shumo]` extra 时才会拉取。
- 历史 `src/notegame` 兼容层仅保留在源码仓库供迁移参考，不再随 PyPI 的 `fungame` 包发布；新代码请直接 `import fungame`。

## 安装

```bash
pip install fungame

# 如果需要运行 shumo 下的建模脚本（依赖 xgboost）：
pip install "fungame[shumo]"
```

## 快速开始

```python
from fungame.games.sudoku.core import sudoku_generate, sudoku_check_solution

# 生成一个 9x9 数独题目（mask_rate 控制挖空比例，默认 0.5）
puzzle = sudoku_generate(mask_rate=0.5)
print(puzzle)

# 校验一个完整数独解是否合法
full_solution = sudoku_generate(mask_rate=0.0)
assert sudoku_check_solution(full_solution.tolist())
```

```python
from fungame.games.nonogram.solver.simpson import FastSolver
from fungame.games.nonogram.core.common import UNKNOWN

# 求解长度为 5、只有一个长度为 3 的色块的一行数织线索
line = [UNKNOWN] * 5
solved = FastSolver.solve([3], line)
print(solved)
```

## 第三方代码与许可证

`fungame.games.nonogram`（`src/fungame/games/nonogram/`）**不是**本组织原创代码，
它派生自第三方开源项目：

| 项目 | 上游地址 | 原始作者 | 原始协议 |
| --- | --- | --- | --- |
| pynogram | <https://github.com/tsionyx/pynogram> | Ivan L (tsionyx) | Apache License 2.0 |

- 该子包在本仓库中的使用范围：重命名顶层包、移除 `six` 兼容层、日志改用 `farlog`、
  用 `functools.lru_cache` 替换已不可用的 `memoized`，并随 `fungame` 一起发布。
  完整的变更说明见 [`src/fungame/games/nonogram/NOTICE`](src/fungame/games/nonogram/NOTICE)，
  Apache-2.0 全文见 [`src/fungame/games/nonogram/LICENSE`](src/fungame/games/nonogram/LICENSE)。
- `examples/nonogram/` 是上游项目的文档、示例棋盘、基准数据与测试用例，同为 Apache-2.0，
  仅作参考保留在源码仓库，不参与构建与发布（见 [`examples/nonogram/NOTICE`](examples/nonogram/NOTICE)）。

因此 `fungame` 发行包的整体许可证是 `MIT AND Apache-2.0`：本组织自己编写的部分
（`games/sudoku`、`games/topwar`、`shumo`、`utils` 等）为 MIT，`games/nonogram`
保持上游的 Apache-2.0。

## 关于 farfarfun

[farfarfun](https://github.com/farfarfun) 是一个专注于实用工具库的开源组织，
涵盖云存储、数据处理、AI、多媒体与开发工具链等方向。

- 🏠 组织主页：<https://github.com/farfarfun>
- 📦 PyPI：<https://pypi.org/user/niuliangtao/>
- 📧 联系：farfarfun@qq.com

本项目自有代码基于 [MIT](LICENSE) 协议开源；`fungame.games.nonogram` 子包沿用上游
pynogram 的 [Apache License 2.0](src/fungame/games/nonogram/LICENSE)，详见上文「第三方代码与许可证」。
