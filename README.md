# fungame

这是一个游戏相关代码的杂货仓库（umbrella 仓库），把几个互不相关的小项目放在一起维护，**不是**一个统一封装的游戏 SDK。

- `src/fungame/games/` 下是实际代码：
  - `fungame.games.nonogram` —— 数织（Nonogram）自动求解器，含棋盘建模、多种求解算法（`solver/bgu.py`、`solver/simpson.py`、`solver/machine.py` 等）和 ASCII 渲染器。
  - `fungame.games.sudoku` —— 数独的生成/求解代码（`Sudoku` 类 + `sudoku_generate` / `sudoku_solve_solution` 等函数）。
  - `fungame.games.topwar` —— 针对手游《Top War》的自动化脚本（实体建模、请求/响应封装、任务/礼包码等），依赖 `funsecret` 中预先配置好的账号凭据。
  - `fungame.shumo` —— 一次数学建模比赛（UWB 定位数据分析）的解题脚本，属于一次性代码，未再维护；相关的 `xgboost` 依赖只在安装 `fungame[shumo]` extra 时才会拉取。
- `src/notegame/` 是一层把 `notegame` 前缀转发到 `fungame` 的兼容模块，只存在于源码仓库，不随 PyPI 的 `fungame` 包发布；导入路径一律写 `fungame`（详见下文「`notegame` 前缀的兼容层」）。

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

## `notegame` 前缀的兼容层

`src/notegame/` 下的转发模块让 `import notegame` 仍然可用：它发出
`DeprecationWarning` 后转发到 `fungame`，模块路径与 API 一一对应，把前缀换掉即可。

```python
from notegame.games.sudoku.core import sudoku_generate   # 已废弃
from fungame.games.sudoku.core import sudoku_generate    # 用这个
```

- **不随包发布**：这层转发只存在于源码仓库，`pip install fungame` 装不到它
  （见 `pyproject.toml` 的 `[tool.hatch.build.targets.wheel]`）。
- **移除版本**：将在 **`fungame 2.0.0`** 中删除。
- **PyPI 上的 `notegame` 是另一个发行包**：最新版 `0.5.18`（2021-12-02），
  只声明 `tqdm` 一个依赖，既不依赖也不转发到 `fungame`，装到的是一套独立的旧代码。
  要用本仓库的 API 只能装 `fungame`。是否给 `notegame` 补发一个转发版属于仓库
  所有者的发布决策，跟踪见
  [farfarfun/todo-list](https://github.com/farfarfun/todo-list/issues)。

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
