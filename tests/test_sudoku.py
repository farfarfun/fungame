"""sudoku 模块的正常/边界用例测试。"""

import copy

import numpy as np
import pytest

from fungame.games.sudoku import (
    Sudoku,
    SudokuUnsolvableError,
    sudoku_check_solution,
    sudoku_generate,
    sudoku_solve_solution,
)
from fungame.games.sudoku.core import (
    _generate_full_grid,
    sudoku_solve_solution1,
    sudoku_solve_solution2,
)

# 一个已知合法、填满的 9x9 数独解（作为真值基准）。
SOLVED_GRID = [
    [5, 3, 4, 6, 7, 8, 9, 1, 2],
    [6, 7, 2, 1, 9, 5, 3, 4, 8],
    [1, 9, 8, 3, 4, 2, 5, 6, 7],
    [8, 5, 9, 7, 6, 1, 4, 2, 3],
    [4, 2, 6, 8, 5, 3, 7, 9, 1],
    [7, 1, 3, 9, 2, 4, 8, 5, 6],
    [9, 6, 1, 5, 3, 7, 2, 8, 4],
    [2, 8, 7, 4, 1, 9, 6, 3, 5],
    [3, 4, 5, 2, 8, 6, 1, 7, 9],
]


def _make_puzzle_from_solved(solved):
    """在一个已解出的网格基础上，每行挖掉一个格子，构造出可解的题目。"""
    puzzle = copy.deepcopy(solved)
    for r in range(9):
        c = r % 9  # 每行挖掉的列不同，避免挖出的格子凑巧共线
        puzzle[r][c] = 0
    return puzzle


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


@pytest.mark.parametrize("bad_mask_rate", [-0.1, 1.5])
def test_sudoku_generate_invalid_mask_rate_raises(bad_mask_rate):
    """mask_rate 超出 [0, 1] 范围属于非法入参，应报错而不是返回错误结果。"""
    with pytest.raises(ValueError):
        sudoku_generate(mask_rate=bad_mask_rate)


def test_sudoku_object_construction():
    """Sudoku() 应能从带空格的题目正确构造出 9x9 内部网格。"""
    puzzle = _make_puzzle_from_solved(SOLVED_GRID)
    sudo = Sudoku(puzzle)
    assert sudo.value.shape == (9, 9)
    # get_num_count 统计已经是确定整数的格子数量。
    # 每行挖掉一个格子，共挖掉 9 个，所以应剩下 81 - 9 个已确定格子。
    assert sudo.get_num_count() == 81 - 9


def test_sudoku_object_construction_invalid_shape_raises():
    """给 Sudoku() 传入无法整理成 9x9 的数据应直接报错，而不是静默产生错误结果。"""
    with pytest.raises(ValueError):
        Sudoku([1, 2, 3])

    with pytest.raises(ValueError):
        Sudoku([[1, 2], [3, 4]])


def test_sudoku_check_solution_valid_grid():
    """正确填满的网格应被判定为合法解。"""
    assert sudoku_check_solution(SOLVED_GRID) is True


def test_sudoku_check_solution_detects_invalid_board():
    bad = np.zeros((9, 9), dtype=int)
    bad[:] = 1  # 全部填 1，显然不是合法解
    assert sudoku_check_solution(bad.tolist()) is False


def test_sudoku_check_solution_duplicate_in_row():
    """同一行出现重复数字时必须被判定为非法解。"""
    broken = copy.deepcopy(SOLVED_GRID)
    # 第一行是 [5, 3, 4, 6, 7, 8, 9, 1, 2]，把最后一格的 2 改成与第一格相同的 5，
    # 从而破坏「同一行不重复」的约束。
    broken[0][8] = broken[0][0]
    assert sudoku_check_solution(broken) is False


def test_sudoku_check_solution_accepts_csv_path(tmp_path):
    """sudoku_check_solution() 的公开入参还支持 CSV 文件路径，应能正确读取并校验。"""
    csv_path = tmp_path / "solved.csv"
    csv_path.write_text("\n".join(",".join(str(v) for v in row) for row in SOLVED_GRID))
    assert sudoku_check_solution(str(csv_path)) is True


@pytest.mark.timeout(30)
def test_sudoku_solve_solution_matches_expected():
    """sudoku_solve_solution() 默认（method=1，Sudoku 类回溯）应能还原出原始解。"""
    puzzle = _make_puzzle_from_solved(SOLVED_GRID)
    solved = sudoku_solve_solution(puzzle)

    solved_list = [[int(v) for v in row] for row in np.array(solved).tolist()]
    assert solved_list == SOLVED_GRID

    # 同时用另一个公开 API 交叉验证，增加鲁棒性。
    assert sudoku_check_solution(solved_list) is True


@pytest.mark.timeout(30)
def test_sudoku_solve_solution_method2_matches_expected():
    """method=2（最少候选数优先的随机填数策略）在给定题目下也应得到正确解。"""
    puzzle = _make_puzzle_from_solved(SOLVED_GRID)
    solved = sudoku_solve_solution(puzzle, method=2)

    solved_list = [[int(v) for v in row] for row in np.array(solved).tolist()]
    assert solved_list == SOLVED_GRID
    assert sudoku_check_solution(solved_list) is True


@pytest.mark.timeout(30)
def test_sudoku_solve_solution_method2_accepts_flat_array_and_csv_path(tmp_path):
    """method=2 的公开输入支持长度为 81 的数组及 CSV 文件路径。"""
    puzzle = _make_puzzle_from_solved(SOLVED_GRID)
    flat_puzzle = [value for row in puzzle for value in row]
    csv_path = tmp_path / "puzzle.csv"
    csv_path.write_text(
        "\n".join(",".join(str(value) for value in row) for row in puzzle)
    )

    for input_value in (flat_puzzle, str(csv_path)):
        solved = sudoku_solve_solution(input_value, method=2)
        assert np.array(solved).tolist() == SOLVED_GRID


@pytest.mark.timeout(30)
def test_sudoku_solve_solution_unsolvable_puzzle_raises():
    """无解的题目（给定数字本身就互相矛盾）求解时应抛出领域异常 SudokuUnsolvableError。"""
    # 第一行放两个相同的数字 5，直接构成矛盾，确定无解。
    unsolvable = [
        [5, 5, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
    ]
    with pytest.raises(SudokuUnsolvableError):
        sudoku_solve_solution(unsolvable, method=1)


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
