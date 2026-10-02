"""
程序入口：演示如何用 nonogram 求解器在终端求解并渲染一个棋盘。
"""

import json
import sys
from typing import Any

from farlog import getLogger

from fungame.games.nonogram.core.backtracking import Solver
from fungame.games.nonogram.core.board import NumpyBlackBoard, make_board
from fungame.games.nonogram.core.renderer import BaseAsciiRenderer
from fungame.games.nonogram.reader import read_example

logger = getLogger("fungame")


def solve(
    d_board: NumpyBlackBoard,
    draw_final: bool = False,
    draw_probes: bool = False,
    **solver_args: Any,
) -> None:
    """求解给定棋盘，并在求解失败或结束时负责渲染结果。

    :param d_board: 待求解的棋盘实例。
    :param draw_final: 是否只在求解流程结束后画一次最终结果（不逐步渲染过程）。
    :param draw_probes: 是否在求解结束后输出求解器探测过程的调试信息。
    :param solver_args: 透传给 `Solver` 的额外求解参数。
    :return: 无返回值；棋盘的求解与渲染结果通过 `d_board` 的副作用体现。
    :raises Exception: 求解过程中抛出的异常会在完成清理渲染后原样向上抛出。
    """

    if not draw_final:
        d_board.on_solution_round_complete = lambda board: board.draw()
        if d_board.has_blots:
            d_board.on_row_update = lambda index, board: board.draw()
            d_board.on_column_update = lambda index, board: board.draw()

    solver = Solver(d_board, **solver_args)

    try:
        solver.solve()
    finally:
        # 求解失败（异常向上传播）或要求只画最终结果时，都需要补画一次棋盘。
        # 用 sys.exc_info() 判断"当前是否正在异常传播中"，
        # 这样无需捕获异常本身即可完成清理逻辑，异常会原样继续向上抛出。
        exc_in_progress = sys.exc_info()[0] is not None
        if exc_in_progress or draw_final:
            d_board.draw()

        if not d_board.is_solved_full:
            d_board.draw_solutions()

        if draw_probes and solver.search_map:
            logger.info(json.dumps(solver.search_map.to_dict(), indent=1))


def draw_solution(board_def: tuple, draw_final: bool = False, **solver_args: Any) -> None:
    """在终端中以动画形式求解给定棋盘定义。

    :param board_def: `(columns, rows)` 形式的棋盘列/行约束定义。
    :param draw_final: 是否只在求解结束后画一次最终结果。
    :param solver_args: 透传给 `solve` 的额外求解参数。
    :return: 无返回值，求解过程与结果直接渲染到终端。
    """
    d_board = make_board(*board_def, renderer=BaseAsciiRenderer)

    solve(d_board, draw_final=draw_final, **solver_args)


def main() -> None:
    """示例入口：求解一个内置的 nonogram 棋盘并在终端渲染。"""
    columns = [[7], [1], [1], [1], [7], [0],
               [3], [1, 1, 1], [1, 1, 1], [2], [0],
               [6], [0],
               [6], [0],
               [3], [1, 1], [5], [1, 1], [3], [0],
               [5, 1], ]
    rows = [[1, 1, 1],
            [1, 1, 1, 1, 1],
            [1, 1, 2, 1, 1, 3, 1],
            [5, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 4, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 2, 1, 1, 3, 1], ]

    board_def = read_example("hello.txt")
    board_def = (columns, rows)
    draw_solution(board_def)


if __name__ == '__main__':
    main()
