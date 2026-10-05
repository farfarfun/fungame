# 更新日志

本文件记录 `fungame` 的重要变更，格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，按版本倒序排列。

> **发布状态说明**：`pyproject.toml` 当前声明 `1.0.9`，但 PyPI 上 `fungame` **只有
> `1.0.1` 一个发行版**（2024-10-26）。`1.0.2`~`1.0.9` 只是仓库里的版本号递增，
> 从未发布，因此不单列版本条目——这些版本区间内的全部改动都归在下面的「未发布」里，
> 等下一次真正发版时再一起落到对应版本号下。

## [未发布]

### 新增

- `tests/test_sudoku.py`、`tests/test_nonogram.py`：补充 sudoku/nonogram 公开 API 的正常与边界用例测试。
- `pyproject.toml` 新增 `shumo` extra（`xgboost`），仅在运行一次性建模脚本时才需要安装。
- `pyproject.toml` 补全实际使用到的运行时依赖（`farlog`、`funshell`、`pandas`、`pillow`、`tqdm`、`websocket-client`）及版本下限。
- `tests/test_topwar.py`：补充 `topwar` 请求构造/响应解析的正常路径，以及凭据读取失败、WebSocket 发送失败等边界与失败路径用例。
- `tests/test_shumo.py`：补充 `shumo.load_data`/`shumo.entity`/`shumo.solution`（不依赖可选的 `xgboost`）的正常与边界用例测试。
- 补齐第三方代码 `pynogram` 的许可证与来源声明：新增 `src/fungame/games/nonogram/LICENSE`（Apache-2.0 全文）与同目录 `NOTICE`（版权声明 + Apache-2.0 §4(b) 要求的变更说明），`examples/nonogram/` 同样补上 `LICENSE` 与 `NOTICE`；通过 `pyproject.toml` 的 `license-files` 把它们纳入发行包。
- README 新增「第三方代码与许可证」小节，列出 `fungame.games.nonogram` 的上游地址、原始作者、原始协议与本仓库的使用范围。
- README 新增「从 notegame 迁移」小节，给出新旧包名对照、导入前缀替换方式、兼容层移除版本与当前已知缺口。
- `tests/`：补充 3 个本轮缺陷的回归测试（彩色线索归一化不再 `NameError`、`load_all_and_merge` 自动建目录、`check_data` 逐列标注离群点）。

### 修复

- 修复 `pyproject.toml` 中 `funsecret` 版本下限过低（`>=1.4.0`）、未达到组织推荐基线的问题，升级为 `>=1.4.84`。
- 修复 `shumo/solution.py`、`shumo/model.py` 用 `print()` 输出中间调试信息的问题，统一改用 `farlog` 日志。
- 修复 `games/nonogram/main.py` 中 `except BaseException: ...; raise` 的过宽异常捕获写法，改为在 `finally` 中用 `sys.exc_info()` 判断异常是否正在传播，无需实际捕获即可完成清理逻辑；同时移除该文件残留的 `print()` 调用，补全类型标注与中文 docstring。
- 补全 `games/topwar/server/action.py`、`games/topwar/entity/request.py` 公开类与方法的类型标注及中文 docstring，并清理其中已失效的注释代码。
- 修复 `topwar` 模块中把账号 token / UUID 等凭据通过 `print()` 输出到标准输出的问题，改为不记录敏感值的日志。
- 修复 `sudoku_generate()` 使用无回溯的贪心随机填数算法、实际上几乎不可能生成一个完整合法数独解（会长时间挂起）的问题，改用标准的分块随机置换算法一次性生成合法解。
- 修复全仓库 `print()` 充当日志使用、裸 `except Exception`/`except:` 吞异常的问题：统一改用 `farlog` 输出日志，按具体异常类型捕获，并通过 `raise ... from err` 或 `logger.exception()` 保留原始异常上下文。
- 修复 ADB/截图相关代码直接使用 `os.popen`/`subprocess` 的问题，改用组织统一的 `funshell.run_shell`。
- 修复 `topwar/core/db.py` 依赖已废弃的 `notedrive.tables.SqliteTable` 的问题，改为基于标准库 `sqlite3` 的最小实现，不再引入额外第三方依赖。
- 修复日志迁移到 `farlog`（底层为 loguru）后，遗留的 `%s`/`%d`/`%r` 风格旧式日志参数不会被正确插值、导致日志消息里出现字面 `%s` 的问题，统一改为 `{}` 风格。
- 修复 README 中声称 `pyproject.toml` 依赖 `fungame-sudoku>=1.0.2` 但实际并未声明该依赖的不实描述。
- 修复 `memoized` 第三方库在 Python 3.11+ 上因 `inspect.getargspec` 被移除而导致 `fungame.games.nonogram` 全部无法导入的问题，改用标准库 `functools.lru_cache`。
- 补漏此前 `%s`→`{}` 迁移遗漏的一处混用写法：`games/nonogram/core/backtracking.py` 的 `logger.warning('Contradictions (found {}): %f', ...)` 第二个占位符仍是 `%f`，同样会被静默丢弃，改为 `{}`。
- 修复 `games/nonogram/core/color.py` 的 `normalize_description_colored` 缺少 `normalize_description` / `BlottedBlock` 的函数内延迟导入（vendoring 上游 pynogram 时漏掉了这一行），导致该函数一被调用就抛 `NameError` 的问题；彩色数织线索此前完全无法归一化。
- 修复 `games/sudoku/core.py` 的 `sudoku_solve_solution2` 随机重试没有上限、遇到无解题面会永久挂起的问题，改为 `max_attempts`（默认 1000）轮后抛 `ValueError`。
- 修复 `shumo/load_data.py` 中 `assert len(d41) == len(d41)` 把 `d42` 漏写成 `d41` 的问题，`distance_check` 透视表行数对不上时该断言形同虚设。
- 修复 `shumo/load_data.py` 的 `load_all_and_merge` 写 CSV 前不创建目标目录的问题（默认目标是相对路径 `data/<目录名>.csv`，目录不存在就直接 `FileNotFoundError`）；同时把 `to_csv(index=None)` 改为语义正确的 `index=False`，两处裸 `open()` 改为 `with`。
- 修复 `shumo/entity.py` 的 `check_data` 内部 `check_field` 按传入 `field` 取分位数、却一律按 `dis_0` 判断的问题：等于把 `dis_0` 重复检查了四遍，`dis_1`~`dis_3` 上的离群点永远不会被标记。
- 修复 `games/topwar/core/db.py` 中 `super().__init__(db_path=..., *args, **kwargs)` 把星号实参排在关键字实参之后（`B026`）的问题，一旦传入位置参数就会 `TypeError: got multiple values for argument`；同时改用 Python 3 的零参 `super()`。
- 修复 `pyproject.toml` 把整个发行包声明为 `license = "MIT"`、但实际随包分发了 Apache-2.0 的 pynogram 派生代码的问题，更正为 SPDX 表达式 `MIT AND Apache-2.0`。

### 变更

- `notegame` 兼容层不再随 `fungame` 发布；源码仍保留用于迁移旧调用方。
- 移除 `six` 兼容库：仓库 `requires-python>=3.10`，不再需要 Python 2/3 兼容层，相关 `iteritems`/`itervalues`/`string_types`/`six.moves.*`/`@add_metaclass` 等用法均已改为原生 Python 3 写法。
- `sudoku/core.py` 公开函数补全类型标注（`sudoku_generate`、`sudoku_check_solution`、`sudoku_solve_solution1/2` 等）与中文 docstring（用途、参数、返回值、异常）。
- 删除未被引用、依赖已废弃 `noteodps` 的调试脚本 `topwar/test.py`。
- `shumo/load_data.py`、`shumo/entity.py` 补齐模块级说明、公开函数/类的类型标注与中文 docstring；删除与 `TagInfo` 完全重复、无任何引用的 `TagInfoBak1`；在 `check_data` 中写明「三角不等式那一档（`normal=3`）当年被手工注释掉、实际从不触发」这一既有事实（行为保持不变）。
- `games/nonogram/solver/simpson.py` 的 `FastSolver` 及 `push_left` / `push_right` / `_solve` 英文 docstring 改为中文，并注明派生自上游 pynogram；修正 `solver/base.py` 中 `_error_message` 误抄 `solve` 的 docstring。

### 废弃

- `src/notegame` 兼容层：`import notegame` 已废弃，替代品为 `import fungame`（模块路径一一对应，把前缀换掉即可）。弃用警告、README「从 notegame 迁移」小节与本条目统一声明：**该兼容层将在 `fungame 2.0.0` 中移除**，在此之前保留。
  - 已知缺口：PyPI 上独立的 `notegame` 发行包停留在 2021 年的 `0.5.18`，不会转发到 `fungame`；是否补发一个最终版 `notegame` 转发包属于发布决策，需仓库所有者确认。

## [1.0.1] - 2024-10-26

当前 PyPI 上 `fungame` 唯一一个已发布版本。

### 新增

- 首次以 `fungame` 名义发布，内容为原 `notegame` 仓库的代码。

### 已知问题

- 该发行版实际仍把全部代码打在顶层 `notegame/` 包下，另外附带一个**空的**
  `fungame/__init__.py`。这个 `__init__.py` 会使 `fungame` 变成常规包，
  从而屏蔽掉 `fungame-sudoku` 等同名命名空间包（PEP 420）的内容。
- 该发行版未声明任何运行时依赖，`Summary` 仍是模板占位文案
  `Add your description here`。
- 仓库内从 `1.0.2` 起的改动（包括移除空 `__init__.py`、补全依赖、改名到
  `fungame.*` 导入路径）都还没有发布，README 里的快速开始示例对
  `pip install fungame` 装到的 `1.0.1` 并不成立。
