# fungame

这是一个游戏相关代码的杂货仓库（umbrella 仓库），把几个互不相关的小项目放在一起维护，**不是**一个统一封装的游戏 SDK。

- `src/fungame/games/` 下是实际代码：
  - `fungame.games.nonogram` —— 数织（Nonogram）自动求解器，含棋盘建模、多种求解算法（`solver/bgu.py`、`solver/simpson.py`、`solver/machine.py` 等）和 ASCII 渲染器。
  - `fungame.games.sudoku` —— 数独的生成/求解代码（`Sudoku` 类 + `sudoku_generate` / `sudoku_solve_solution` 等函数）。
  - `fungame.games.topwar` —— 针对手游《Top War》的自动化脚本（实体建模、请求/响应封装、任务/礼包码等），依赖 `funsecret` 中预先配置好的账号凭据。
  - `fungame.shumo` —— 一次数学建模比赛（UWB 定位数据分析）的解题脚本，属于一次性代码，未再维护；相关的 `xgboost` 依赖只在安装 `fungame[shumo]` extra 时才会拉取。
- 历史 `src/notegame` 兼容层仅保留在源码仓库供迁移参考，不再随 PyPI 的 `fungame` 包发布；新代码请直接 `import fungame`（详见下文「从 notegame 迁移」）。

## 安装

```bash
# 当前仓库的 1.0.9 尚未发布；从源码安装以使用下文示例中的 API：
pip install .

# 如果需要运行 shumo 下的建模脚本（依赖 xgboost）：
pip install ".[shumo]"
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

## 从 notegame 迁移

本仓库早期叫 `notegame`，后整体改名为 `fungame`。

| | 旧 | 新 |
| --- | --- | --- |
| 发行包名 | `notegame` | `fungame` |
| 安装方式 | `pip install notegame` | `pip install fungame` |
| 导入前缀 | `import notegame` | `import fungame` |

迁移只需把导入前缀从 `notegame` 换成 `fungame`，模块路径与 API 一一对应：

```python
# 旧
from notegame.games.sudoku.core import sudoku_generate
# 新
from fungame.games.sudoku.core import sudoku_generate
```

- **兼容层范围**：`src/notegame/` 下的转发模块会发出 `DeprecationWarning`，
  但它**只存在于源码仓库**，`pip install fungame` 装不到。
- **移除版本**：该兼容层将在 **`fungame 2.0.0`** 中删除。
- **已知缺口**：PyPI 上独立的 `notegame` 发行包停留在 2021 年的 `0.5.18`，
  不会自动转发到 `fungame`，旧用户必须手工改成 `pip install fungame`。
  是否再发一个最终版 `notegame` 转发包属于仓库所有者的发布决策，
  跟踪见 [farfarfun/todo-list](https://github.com/farfarfun/todo-list/issues)。

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

本项目以 MIT 协议发布；`games/nonogram` 子包继续保留上游的 Apache-2.0
许可证、版权声明和 NOTICE。

## 关于 farfarfun

[farfarfun](https://github.com/farfarfun) 是一个专注于实用工具库的开源组织，
涵盖云存储、数据处理、AI、多媒体与开发工具链等方向。

- 🏠 组织主页：<https://github.com/farfarfun>
- 📦 PyPI：<https://pypi.org/user/niuliangtao/>
- 📧 联系：farfarfun@qq.com

本项目基于 [MIT](LICENSE) 协议开源。
