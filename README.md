# fungame

这是一个游戏相关代码的杂货仓库（umbrella 仓库），把几个互不相关的小项目放在一起维护，**不是**一个统一封装的游戏 SDK。

- `src/fungame/__init__.py` 目前是空文件——顶层 `fungame` 包本身不提供任何功能。
- 实际代码都在 `src/notegame/games/` 下，沿用的是组织改名前的 `note*` 命名，没有跟着仓库一起改成 `fungame`：
  - `notegame.games.nonogram` —— 数织（Nonogram）自动求解器，含棋盘建模、多种求解算法（`solver/bgu.py`、`solver/simpson.py`、`solver/machine.py` 等）和 ASCII 渲染器，`examples/nonogram` 下有对应的单元测试。
  - `notegame.games.sudoku` —— 数独的生成/求解代码（`Sudoku` 类 + `sudoku_generate` / `sudoku_solve_solution` 等函数）。
  - `notegame.games.topwar` —— 针对手游《Top War》的自动化脚本（实体建模、请求/响应封装、任务/礼包码等）。
  - `notegame.shumo` —— 一次数学建模比赛（UWB 定位数据分析）的解题脚本，属于一次性代码，未再维护。

## 关于 `fungame-sudoku` 依赖

`pyproject.toml` 声明了 `fungame-sudoku>=1.0.2` 依赖，但仓库源码里**没有任何地方 `import` 它**——数独功能用的是上面提到的自带的 `notegame.games.sudoku`，这是两套独立的数独实现。也就是说，装了 `fungame` 并不会让你直接用到 `fungame-sudoku` 那个包的 API，这里如实说明，避免误解。

## 已知问题

- `notegame.games.*` 下大量文件（nonogram、sudoku 等）`import notetool.tool.log` 做日志，但 `notetool` 并未出现在 `pyproject.toml` 的依赖列表里，仅安装 `fungame` 大概率会因为缺依赖而导入失败。
- `notegame/games/sudoku/core.py` 里使用了 `np.int`，该别名已在 NumPy 1.24+ 中移除，在较新的 NumPy 版本下会直接报错。

## 安装

```bash
pip install fungame
```

（如上所述，实际能否正常 `import` 依赖是否额外装了 `notetool` 等未声明的包，请自行验证。）
