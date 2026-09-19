"""nonogram 模块的正常/边界用例测试，覆盖 reader/core/solver 的公开能力。"""
import tempfile
from pathlib import Path

import pytest

from fungame.games.nonogram.core.common import BOX, SPACE, UNKNOWN, partial_sums
from fungame.games.nonogram.reader import parse_line, read_ini
from fungame.games.nonogram.solver.base import cache_info
from fungame.games.nonogram.solver.bgu import BguSolver
from fungame.games.nonogram.solver.machine import ReverseTrackingSolver
from fungame.games.nonogram.solver.simpson import FastSolver
from fungame.games.nonogram.utils.other import from_two_powers, is_close, two_powers
from fungame.games.nonogram.utils.priority_dict import PriorityDict


def test_parse_line_splits_and_strips():
    assert parse_line("1, 2, 3") == ["1", "2", "3"]
    assert parse_line("'a', \"b\"") == ["a", "b"]


def test_parse_line_trailing_comma():
    assert parse_line("1,2,3,") == ["1", "2", "3"]


def test_read_ini_parses_board_definition():
    content = (
        "[clues]\n"
        "columns = 1\n"
        "          2\n"
        "rows = 1\n"
        "       2\n"
    )
    with tempfile.TemporaryDirectory() as tmp_dir:
        board_file = Path(tmp_dir) / "board.txt"
        board_file.write_text(content, encoding="utf-8")
        columns, rows = read_ini(str(board_file))
    assert columns == ["1", "2"]
    assert rows == ["1", "2"]


@pytest.mark.parametrize("solver_cls", [FastSolver, BguSolver, ReverseTrackingSolver])
def test_line_solvers_solve_simple_block(solver_cls):
    # 长度为 5 的行，只有一个大小为 3 的色块，中间的格子必然是 BOX
    line = [UNKNOWN] * 5
    description = [3]
    solved = solver_cls.solve(description, line)
    assert len(solved) == 5
    assert solved[2] == BOX


def test_line_solvers_solve_fully_specified_line():
    # 整行都是色块的情况（无歧义）
    line = [UNKNOWN] * 3
    description = [3]
    solved = FastSolver.solve(description, line)
    assert list(solved) == [BOX, BOX, BOX]


def test_line_solvers_solve_all_space_line():
    # description 为空，整行应全是 SPACE
    line = [UNKNOWN] * 4
    solved = FastSolver.solve([], line)
    assert list(solved) == [SPACE] * 4


def test_base_line_solver_cache_info_tracks_solvers():
    info = cache_info()
    assert "BaseLineSolver" in info
    assert "FastSolver" in info
    for size, hit_rate in info.values():
        assert size >= 0
        assert 0.0 <= hit_rate <= 1.0


def test_partial_sums_boundary_empty_description():
    assert list(partial_sums([], colored=False)) == []


def test_partial_sums_normal_case():
    # 每个色块之间至少留一个空格，因此从第二个色块起累加时会 +1
    result = list(partial_sums([1, 2], colored=False))
    assert result == [1, 4]


def test_two_powers_and_from_two_powers_roundtrip():
    assert two_powers(42) == (2, 8, 32)
    assert from_two_powers([2, 8, 32]) == 42


def test_two_powers_zero_is_empty():
    assert two_powers(0) == ()


def test_is_close_normal_and_boundary():
    assert is_close(1.0, 1.0 + 1e-10)
    assert not is_close(1.0, 1.1)
    assert is_close(0.0, 0.0)


def test_priority_dict_pop_smallest_returns_in_priority_order():
    pd = PriorityDict({"a": 3, "b": 1, "c": 2})
    assert pd.pop_smallest() == ("b", 1)
    assert pd.pop_smallest() == ("c", 2)
    assert pd.pop_smallest() == ("a", 3)
    with pytest.raises(IndexError):
        pd.pop_smallest()
