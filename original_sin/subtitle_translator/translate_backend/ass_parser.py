import logging
from typing import Tuple, List, Any

from .base import SubtitleParser, Value

logger = logging.getLogger(__name__)


class AssValue(Value):
    def _from_str(self, s: str):
        s = s.replace(r'\N', '')
        op = '{'
        cl = '}'
        while s:
            have_bracket = op in s and cl in s

            if have_bracket:
                bracket_start = s.index(op)
                bracket_end = s.index(cl)
                s = self.cut_brackets(bracket_start, bracket_end + 1, s)
            else:
                self.append(s)
                s = ''

    def cut_brackets(self, start, end, s):
        pre_tile, tile = s[:start], s[start: end]
        s = s[end:]
        if pre_tile:
            self.append(pre_tile)
        self.append(self.raw_token(tile))
        return s


class AssParser(SubtitleParser):
    file_ext = '.ass'

    row_value_class = AssValue

    def _parse(self, file) -> Tuple[str, List[Any], str]:
        find = '[Events]'
        assert find in file, f'Is not .ass file `{file[:100]}`'
        pos = file.index(find) + len(find) + 1
        pre, data = file[:pos], file[pos:]
        end = ''

        data = data.split('\n')
        num = data[0].count(',')  # Format: ...
        pre += f'\n{data.pop(0)}'
        rows = []

        def index_with_counter(_row):
            index = 0
            if row:
                for _ in range(num):
                    index = _row.index(',', index) + 1
            return index
        for row in data:
            pos = index_with_counter(row)
            row = self.row_class(
                pre_val=row[:pos],
                value=AssValue(row[pos:]),
                post_val=''
            )
            # logger.info(f'[{row.pre_val}][{row.value}][{row.post_val}]')
            rows.append(row)
        return pre, rows, end

