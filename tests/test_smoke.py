"""轻量冒烟测试：仅验证包能正常导入、核心可用面能被调用一次。"""
import pytest


def test_import_fungame():
    import fungame  # noqa: F401


def test_import_fungame_games_sudoku():
    # 真正的游戏逻辑代码已经从 notegame.* 迁移到 fungame.* 下。
    from fungame.games.sudoku import sudoku_generate

    puzzle = sudoku_generate()
    assert puzzle.shape == (9, 9)


def test_import_notegame_compat_shim_warns_and_aliases():
    # `notegame` 是废弃的兼容层，转发到 `fungame`，并给出 DeprecationWarning。
    # 注意：`notegame/__init__.py` 的 warnings.warn() 只在模块首次被执行时触发一次，
    # 之后 `import notegame` 命中 sys.modules 缓存不会重复告警，所以这个测试必须是
    # 本文件里第一个 `import notegame` 的地方。
    with pytest.deprecated_call():
        import notegame

    import fungame

    assert notegame is fungame


def test_import_notegame_games_sudoku_compat():
    # 沿用旧的 `notegame.games.sudoku` 导入路径依然可用（走的是上面缓存的别名）。
    from notegame.games.sudoku import sudoku_generate

    puzzle = sudoku_generate()
    assert puzzle.shape == (9, 9)
