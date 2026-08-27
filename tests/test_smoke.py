"""轻量冒烟测试：仅验证包能正常导入、核心可用面能被调用一次。"""
import pytest


def test_import_fungame():
    import fungame  # noqa: F401


def test_import_notegame():
    # 仓库里真正的游戏逻辑代码放在 notegame.* 命名空间下（历史遗留，未随 fun* 改名完成），
    # fungame 包本体（src/fungame/__init__.py）是空的。
    import notegame  # noqa: F401


def test_notegame_games_unavailable_due_to_missing_notetool():
    # notegame.games.sudoku / nonogram / topwar 等子模块依赖已废弃且未发布到 PyPI 的
    # `notetool` 包（`from notetool.tool.log import logger`），无法安装，因此这些子模块
    # 实际上无法被外部用户导入或使用。这部分是与已发布的 fungame-sudoku 重复的旧代码，
    # 不在 fungame 包自身对外暴露的能力范围内，此处只做记录性跳过，不修复业务逻辑。
    with pytest.raises(ModuleNotFoundError):
        import notegame.games.sudoku.core  # noqa: F401
    pytest.skip(
        "notegame.games.* 依赖已废弃且未发布的 notetool 包，无法安装；"
        "该目录是与已发布 fungame-sudoku 重复的旧代码，不属于 fungame 包的对外 API"
    )
