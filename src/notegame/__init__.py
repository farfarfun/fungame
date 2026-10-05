"""兼容层：`import notegame` 已废弃，请改用 `import fungame`。

这个模块只做一件事：把 `notegame` 转发到 `fungame`，保证已经在用
`import notegame` / `from notegame...` 的代码在升级后不会立刻报错。

迁移方式：把所有 `notegame` 前缀换成 `fungame` 即可，模块路径与 API 一一对应，
例如 `from notegame.games.sudoku.core import sudoku_generate` 改为
`from fungame.games.sudoku.core import sudoku_generate`。

移除计划：本兼容层将在 `fungame 2.0.0` 中删除，在那之前保留不动。

注意：这个兼容层只存在于源码仓库，`pip install fungame` 装不到它
（见 `pyproject.toml` 的 `[tool.hatch.build.targets.wheel] packages`）。
PyPI 上独立的 `notegame` 发行包停留在 2021 年的 0.5.18，并不会转发到 `fungame`。
"""

import sys
import warnings

import fungame

#: 兼容层计划移除的 `fungame` 版本号，README 与 CHANGELOG 中引用同一个值。
REMOVED_IN = "2.0.0"

warnings.warn(
    "`import notegame` 已废弃，请改用 `import fungame`（模块路径一一对应，"
    f"把前缀 notegame 换成 fungame 即可）。这个兼容层将在 fungame {REMOVED_IN} 中移除。",
    DeprecationWarning,
    stacklevel=2,
)

sys.modules[__name__] = fungame
