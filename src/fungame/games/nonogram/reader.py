"""
Defines methods to parse data file with the board defined
"""

import os
import re
from configparser import RawConfigParser

from fungame.games.nonogram.core.color import ColorMap

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

_INLINE_COMMENT_PREFIXES = '#;'


def parse_line(description, inline_comments=_INLINE_COMMENT_PREFIXES):
    """
    Parse a line and correctly add the description(s) to a collection
    """

    # there can be trailing commas if you copy from source code
    descriptions = description.strip(',').split(',')

    # strip all the spaces and quotes
    descriptions = [desc.strip().strip("'").strip('"').strip()
                    for desc in descriptions]
    return descriptions


def example_file(file_name=''):
    """
    Returns a path to the examples board in text files
    """
    examples_dir = os.path.join(CURRENT_DIR, 'examples')
    if not file_name:
        return examples_dir

    if os.path.isfile(file_name):
        return file_name

    file_name = os.path.join(examples_dir, file_name)
    if os.path.isfile(file_name):
        return file_name

    txt_file_name = file_name + '.txt'
    if os.path.isfile(txt_file_name):
        return txt_file_name

    # just return the original file name, don't know where is it
    return file_name


def read_example(board_file):
    """Return the board definition for given example name"""
    return read_ini(example_file(board_file))


class MultiLineConfigParser(RawConfigParser, object):
    """
    INI-file parser that allows multiple lines in a value
    to be treated like a list.
    Also adds the ';'-style inline comments (disabled in PY3)

    https://stackoverflow.com/a/11866695/1177288
    """

    def __init__(self, *args, **kwargs):
        # allow '#' or ';' as the start of a comment
        if 'inline_comment_prefixes' not in kwargs:
            kwargs['inline_comment_prefixes'] = _INLINE_COMMENT_PREFIXES

        super().__init__(*args, **kwargs)

    def get_list(self, section, option):
        """Split the value into list, remove empty items"""
        value = self.get(section, option)
        return [x.strip() for x in value.splitlines() if x]


_COLOR_RE = re.compile(r'\((.+)\) (.+)')


def read_ini(content):
    """Return the board definition from an INI-file"""

    parser = MultiLineConfigParser()

    if isinstance(content, str):
        content = open(content)

    parser.read_file(content)

    columns = []
    for col in parser.get_list('clues', 'columns'):
        col = parse_line(col)
        if col is not None:
            columns.extend(col)

    rows = []
    for row in parser.get_list('clues', 'rows'):
        row = parse_line(row)
        if row is not None:
            rows.extend(row)

    res = [columns, rows]

    if parser.has_section('colors'):
        colors = ColorMap()
        for color_name, color_desc in parser.items('colors'):
            match = _COLOR_RE.match(color_desc)
            # TODO: spit some info if not matched

            colors.make_color(color_name, *match.groups())

        if not colors.black_and_white:
            res.append(colors)

    return tuple(res)
