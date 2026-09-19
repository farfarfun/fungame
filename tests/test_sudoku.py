"""sudoku 模块的正常/边界用例测试。"""
import numpy as np

from fungame.games.sudoku.core import (
    _generate_full_grid,
    sudoku_check_solution,
    sudoku_generate,
    sudoku_solve_solution1,
    sudoku_solve_solution2,
)


def test_generate_full_grid_is_valid_solution():
    """_generate_full_grid 生成的完整解应满足数独规则。"""
    grid = _generate_full_grid()
    assert grid.shape == (9, 9)
    assert sudoku_check_solution(grid.tolist()) is True


def test_sudoku_generate_shape_and_mask():
    puzzle = sudoku_generate(mask_rate=0.5)
    assert puzzle.shape == (9, 9)
    # 被挖空的格子应为 0，取值范围应在 0~9 之间
    assert set(np.unique(puzzle)).issubset(set(range(10)))


def test_sudoku_generate_mask_rate_zero_is_full_valid_solution():
    """mask_rate=0 时不挖空任何格子，结果应是一个完整合法解。"""
    puzzle = sudoku_generate(mask_rate=0.0)
    assert 0 not in puzzle
    assert sudoku_check_solution(puzzle.tolist()) is True


def test_sudoku_generate_mask_rate_one_is_all_blank():
    """mask_rate=1 时应挖空所有格子。"""
    puzzle = sudoku_generate(mask_rate=1.0)
    assert np.all(puzzle == 0)


def test_sudoku_check_solution_detects_invalid_board():
    bad = np.zeros((9, 9), dtype=int)
    bad[:] = 1  # 全部填 1，显然不是合法解
    assert sudoku_check_solution(bad.tolist()) is False


def test_sudoku_solve_solution1_solves_generated_puzzle():
    full = _generate_full_grid()
    puzzle = full.copy()
    puzzle[0, 0] = 0  # 只挖一个格子，确保有唯一解、能被简单推理解出
    solved = sudoku_solve_solution1(puzzle.tolist())
    assert sudoku_check_solution(np.array(solved, dtype=int)) is True


def test_sudoku_solve_solution2_returns_valid_full_grid():
    full = _generate_full_grid()
    puzzle = full.copy()
    puzzle[np.random.choice([True, False], size=full.shape, p=[0.3, 0.7])] = 0
    solved = sudoku_solve_solution2(puzzle.tolist())
    assert sudoku_check_solution(solved) is True
