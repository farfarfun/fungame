# fungame

这是一个游戏相关代码的杂货仓库（umbrella 仓库），把几个互不相关的小项目放在一起维护，**不是**一个统一封装的游戏 SDK。

- `src/fungame/games/` 下是实际代码：
  - `fungame.games.nonogram` —— 数织（Nonogram）自动求解器，含棋盘建模、多种求解算法（`solver/bgu.py`、`solver/simpson.py`、`solver/machine.py` 等）和 ASCII 渲染器，`examples/nonogram` 下有对应的单元测试。
  - `fungame.games.sudoku` —— 数独的生成/求解代码（`Sudoku` 类 + `sudoku_generate` / `sudoku_solve_solution` 等函数）。
  - `fungame.games.topwar` —— 针对手游《Top War》的自动化脚本（实体建模、请求/响应封装、任务/礼包码等）。
  - `fungame.shumo` —— 一次数学建模比赛（UWB 定位数据分析）的解题脚本，属于一次性代码，未再维护。
- 旧的 `import notegame` 路径仍然可用，走的是 `src/notegame` 下的兼容层：转发到 `fungame` 并给出 `DeprecationWarning`，计划在下一次破坏性版本中移除。新代码请直接 `import fungame`。

## 关于 `fungame-sudoku` 依赖

`pyproject.toml` 声明了 `fungame-sudoku>=1.0.2` 依赖，但仓库源码里**没有任何地方 `import` 它**——数独功能用的是上面提到的自带的 `fungame.games.sudoku`，这是两套独立的数独实现。也就是说，装了 `fungame` 并不会让你直接用到 `fungame-sudoku` 那个包的 API，这里如实说明，避免误解。

## 安装

```bash
pip install fungame
```
