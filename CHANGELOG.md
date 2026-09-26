# 更新日志

本文件记录 `fungame` 的重要变更，格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，按时间倒序排列。

## [未发布]

### 新增

- `tests/test_sudoku.py`、`tests/test_nonogram.py`：补充 sudoku/nonogram 公开 API 的正常与边界用例测试。
- `pyproject.toml` 新增 `shumo` extra（`xgboost`），仅在运行一次性建模脚本时才需要安装。
- `pyproject.toml` 补全实际使用到的运行时依赖（`farlog`、`funshell`、`pandas`、`pillow`、`tqdm`、`websocket-client`）及版本下限。

### 修复

- 修复 `topwar` 模块中把账号 token / UUID 等凭据通过 `print()` 输出到标准输出的问题，改为不记录敏感值的日志。
- 修复 `sudoku_generate()` 使用无回溯的贪心随机填数算法、实际上几乎不可能生成一个完整合法数独解（会长时间挂起）的问题，改用标准的分块随机置换算法一次性生成合法解。
- 修复全仓库 `print()` 充当日志使用、裸 `except Exception`/`except:` 吞异常的问题：统一改用 `farlog` 输出日志，按具体异常类型捕获，并通过 `raise ... from err` 或 `logger.exception()` 保留原始异常上下文。
- 修复 ADB/截图相关代码直接使用 `os.popen`/`subprocess` 的问题，改用组织统一的 `funshell.run_shell`。
- 修复 `topwar/core/db.py` 依赖已废弃的 `notedrive.tables.SqliteTable` 的问题，改为基于标准库 `sqlite3` 的最小实现，不再引入额外第三方依赖。
- 修复日志迁移到 `farlog`（底层为 loguru）后，遗留的 `%s`/`%d`/`%r` 风格旧式日志参数不会被正确插值、导致日志消息里出现字面 `%s` 的问题，统一改为 `{}` 风格。
- 修复 README 中声称 `pyproject.toml` 依赖 `fungame-sudoku>=1.0.2` 但实际并未声明该依赖的不实描述。
- 修复 `memoized` 第三方库在 Python 3.11+ 上因 `inspect.getargspec` 被移除而导致 `fungame.games.nonogram` 全部无法导入的问题，改用标准库 `functools.lru_cache`。

### 变更

- `notegame` 兼容层不再随 `fungame` 发布；源码仍保留用于迁移旧调用方。
- 移除 `six` 兼容库：仓库 `requires-python>=3.10`，不再需要 Python 2/3 兼容层，相关 `iteritems`/`itervalues`/`string_types`/`six.moves.*`/`@add_metaclass` 等用法均已改为原生 Python 3 写法。
- `sudoku/core.py` 公开函数补全类型标注（`sudoku_generate`、`sudoku_check_solution`、`sudoku_solve_solution1/2` 等）。
- 删除未被引用、依赖已废弃 `noteodps` 的调试脚本 `topwar/test.py`。
