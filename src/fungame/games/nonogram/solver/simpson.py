"""基于「左右极限重叠」的单行数织求解算法。

算法来自 http://www.lancaster.ac.uk/~simpsons/nonogram/ls-fast ，
本文件派生自上游 pynogram（Apache-2.0），见 ../NOTICE。
"""

from farlog import getLogger

from ..core.common import BOX, SPACE, UNKNOWN, NonogramError
from .base import BaseLineSolver

logger = getLogger("fungame")

_SYMBOL_MAP = {
    UNKNOWN: ' ',
    SPACE: '-',
    BOX: '#',
}


class FastSolver(BaseLineSolver):
    """用左右极限重叠法求解单行数织线索的求解器。

    把所有色块先全部靠左挤、再全部靠右挤，两种极端摆法重合的格子就能确定。
    速度很快，但不保证把一行完全解出来——多数情况下只能推进一部分，
    剩下的要靠 :mod:`~fungame.games.nonogram.core.propagation` 反复迭代
    或回溯求解器补齐。

    对外入口是继承自 :class:`~fungame.games.nonogram.solver.base.BaseLineSolver`
    的 ``solve(description, line)`` 类方法（带结果缓存）。
    """

    @classmethod
    def push_left(cls, line, clue):
        """把所有色块尽可能往左挤，返回每个色块能取到的最左起始位置。

        Args:
            line: 当前行的格子序列，元素取值为 ``UNKNOWN`` / ``BOX`` / ``SPACE``。
            clue: 该行的线索，即各个色块的长度序列。

        Returns:
            长度与 ``clue`` 相同的列表，第 ``i`` 项是第 ``i`` 个色块的最左起始下标。

        Raises:
            NonogramError: 线索与当前行的已知格子矛盾，这一行无解。
        """

        line_size = len(line)
        clue_size = len(clue)
        res = [0] * clue_size
        solid = [-1] * clue_size

        # initial state
        current_block = 0

        if clue_size > 0:
            res[current_block] = 0

        logger.info('Pushing clue: {}', ', '.join(map(str, clue)))
        logger.info('Pushing line: >{}<', ''.join(
            _SYMBOL_MAP.get(cell, '?') for cell in line))

        while current_block < clue_size:
            # find first/next non-dot:
            # stop if current_block won't fit into remainder of line

            pos = res[current_block]
            block_size = clue[current_block]

            logger.debug('     start {} >{} {}',
                         current_block, pos, block_size)

            while pos < line_size - block_size:
                cell = line[pos]
                if cell != SPACE:
                    break

                pos += 1

            res[current_block] = pos
            logger.debug('     end {} >{} {}', current_block, pos, block_size)

            # no room left
            if (pos + block_size > line_size) or (line[pos] == SPACE):
                raise NonogramError(
                    'No room left: cannot fit %d-th block' % current_block)

            # assume current position doesn't cover a solid
            solid[current_block] = -1

            # check if the current_block fits in before the next dot;
            # monitor for passing over a solid
            i = 0
            while i < block_size:
                cell = line[pos + i]
                if cell == SPACE:
                    break

                if (solid[current_block] < 0) and (cell == BOX):
                    logger.debug('     solid {} >{}#',
                                 current_block, (pos + i))
                    solid[current_block] = i
                i += 1

            # if a dot was encountered...
            if i < block_size:
                logger.debug('     dot {} >{}-', current_block, (pos + i))

                # if a solid is covered, get an earlier current_block to fit
                if solid[current_block] >= 0:
                    # find an earlier current_block that can be moved to cover the solid
                    # covered by the next current_block without uncovering its own
                    while True:
                        if current_block == 0:
                            raise NonogramError(
                                'All previous blocks cover solids')
                        current_block -= 1
                        if (solid[current_block] < 0) or (
                                res[current_block + 1] + solid[current_block + 1] -
                                clue[current_block] + 1 <=
                                res[current_block] + solid[current_block]):
                            break

                    # set the current_block near to the position of the next current_block,
                    # so that it just overlaps the solid, and try again
                    next_pos = res[current_block + 1]
                    next_solid = solid[current_block + 1]
                    res[current_block] = next_pos + \
                        next_solid - clue[current_block] + 1
                    continue

                # otherwise, simply move to the dot, and try again
                res[current_block] += i
                continue

            # now check to see if the end of the current current_block touches an
            # existing solid - if so, the current_block must be shuffled further to
            # ensure it overlaps the solid, but no solid may emerge from the
            # other end
            pos = res[current_block]

            if pos + block_size < line_size:
                end_block_cell = line[pos + block_size]

                if (end_block_cell == BOX) and (solid[current_block] < 0):
                    solid[current_block] = block_size

                while pos + block_size < line_size:
                    cell = line[pos]
                    if cell == BOX:
                        break
                    end_block_cell = line[pos + block_size]
                    if end_block_cell != BOX:
                        break

                    pos += 1
                    solid[current_block] -= 1

            res[current_block] = pos

            logger.debug('     shuffle {} >{} {}',
                         current_block, pos, block_size)

            # if there's still a solid immediately after the current_block, there's
            # an error, so find an earlier current_block to move
            if pos + block_size < line_size:
                end_block_cell = line[pos + block_size]
                if end_block_cell == BOX:
                    logger.debug('     stretched {} >{}#',
                                 current_block, (pos + i))

                    # find an earlier current_block that isn't covering a solid
                    error_block = current_block
                    while True:
                        if current_block == 0:
                            raise NonogramError(
                                'The %d-th block cannot be stretched' % error_block)
                        current_block -= 1
                        if (solid[current_block] < 0) or (
                                res[current_block + 1] + solid[current_block + 1] -
                                clue[current_block] + 1 <=
                                res[current_block] + solid[current_block]):
                            break

                    # set the current_block near to the position of the next current_block,
                    # so that it just overlaps the solid, and try again
                    next_pos = res[current_block + 1]
                    next_solid = solid[current_block + 1]
                    res[current_block] = next_pos + \
                        next_solid - clue[current_block] + 1
                    continue

            # the current_block is in place, so try the next
            pos = res[current_block] + 1 + clue[current_block]
            if current_block + 1 < clue_size:
                current_block += 1
                res[current_block] = pos
            else:
                # no more blocks, so just check for any remaining solids
                while pos < line_size:
                    cell = line[pos]
                    if cell == BOX:
                        break

                    pos += 1

                # if a solid was found...
                if pos < line_size:
                    logger.debug('     trailing >{}#', pos)

                    # move the current_block so it covers it, but check if solid
                    # becomes uncovered
                    if (solid[current_block] >= 0) and (
                            pos - block_size + 1 > res[current_block] + solid[current_block]):
                        #  a solid was uncovered, so look for an earlier current_block

                        # find an earlier current_block that isn't covering a solid
                        while True:
                            if current_block == 0:
                                raise NonogramError(
                                    'All previous blocks cover solids')
                            current_block -= 1
                            if (solid[current_block] < 0) or (
                                    res[current_block + 1] +
                                    solid[current_block + 1] - clue[current_block] + 1 <=
                                    res[current_block] + solid[current_block]):
                                break

                        # set the current_block near to the position of the next current_block,
                        # so that it just overlaps the solid, and try again
                        next_pos = res[current_block + 1]
                        next_solid = solid[current_block + 1]
                        res[current_block] = next_pos + \
                            next_solid - clue[current_block] + 1

                        continue
                    # if (solid[current_block] >= 0) ... }

                    # solid[current_block] -= pos - block_size + 1 - res[current_block]
                    res[current_block] = pos - block_size + 1
                    continue
                # if pos < line_size ... }
                # no solid found
                current_block += 1
            # if current_block + 1 < clue_size: else ... }
        # while current_block < clue_size ... }
        # all okay
        return res

    @classmethod
    def push_right(cls, line, clue):
        """把所有色块尽可能往右挤，返回每个色块能取到的最右位置。

        实现上是把 ``line`` 与 ``clue`` 同时反转后复用 :meth:`push_left`。

        Args:
            line: 当前行的格子序列。
            clue: 该行的线索，即各个色块的长度序列。

        Returns:
            长度与 ``clue`` 相同的列表，第 ``i`` 项是第 ``i`` 个色块在**反转坐标系**下
            的最左起始下标；调用方需要用 ``len(line) - pos - size`` 换算回正向下标
            （:meth:`_solve` 里就是这么做的）。

        Raises:
            NonogramError: 线索与当前行的已知格子矛盾，这一行无解。
        """
        clue = clue[::-1]
        line = line[::-1]

        return list(reversed(cls.push_left(line, clue)))

    def _solve(self):
        """用左右极限重叠法求解单行，返回推进后的格子序列。

        Returns:
            新的格子列表：左右两种极端摆法都落在色块里的格子标成 ``BOX``，
            都落在空白里的标成 ``SPACE``，其余保持 ``UNKNOWN``。

        Raises:
            NonogramError: 线索与当前行矛盾（由 :meth:`push_left` 抛出）。
        """

        line = self.line
        clue = self.description

        line_size = len(line)
        clue_size = len(clue)

        logger.debug('Line range = {} to {}', 0, line_size - 1)

        if (clue_size == 1) and clue[0] == 0:
            clue_size = 0

        left_positions = self.push_left(line, clue)

        left_desc = []
        for block in range(clue_size):
            left_desc.append('(%s + %s)' %
                             (left_positions[block], clue[block]))
        logger.info('Left: {}', ' '.join(left_desc))
        left_desc = []
        for block in range(clue_size):
            size_now = sum(map(len, left_desc))
            block = (
                '-' * (left_positions[block] - size_now)) + ('#' * clue[block])
            left_desc.append(block)

        desc_size = len(''.join(left_desc))
        left_desc.append('-' * (line_size - desc_size))
        logger.info('Left: >{}<', ''.join(left_desc))

        middle_desc = [_SYMBOL_MAP.get(cell, '?') for cell in line]
        logger.info('Middle: >{}<', ''.join(middle_desc))

        logger.info('Line range = {} to {}', 0, line_size - 1)

        right_positions = self.push_right(line, clue)

        right_desc = []
        for block in range(clue_size):
            right_desc.append('(%s + %s)' %
                              (right_positions[block], clue[block]))
        logger.info('Right: {}', ' '.join(right_desc))
        right_desc = []
        for block in range(clue_size):
            size_now = sum(map(len, right_desc))
            dots = '-' * \
                (line_size - right_positions[block] - clue[block] - size_now)
            solids = '#' * (clue[block])
            block = dots + solids
            right_desc.append(block)

        desc_size = len(''.join(right_desc))
        right_desc.append('-' * (line_size - desc_size))
        logger.info('Right: >{}<', ''.join(right_desc))

        work = list(line)

        j = 0
        for i in range(clue_size):
            right_positions[i] = line_size - right_positions[i] - clue[i]

            k = left_positions[i]
            work[j: k] = [SPACE] * (k - j)

            j = right_positions[i]
            k = left_positions[i] + clue[i]

            work[j: k] = [BOX] * (k - j)

            j = right_positions[i] + clue[i]

        k = line_size
        work[j: k] = [SPACE] * (k - j)

        return work
