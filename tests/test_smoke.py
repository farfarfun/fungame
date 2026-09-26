"""轻量冒烟测试：仅验证包能正常导入、核心可用面能被调用一次。"""


def test_import_fungame():
    import fungame  # noqa: F401


def test_import_fungame_games_sudoku():
    # 真正的游戏逻辑代码已经从 notegame.* 迁移到 fungame.* 下。
    from fungame.games.sudoku import sudoku_generate

    puzzle = sudoku_generate()
    assert puzzle.shape == (9, 9)
