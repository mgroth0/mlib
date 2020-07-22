from dataclasses import dataclass
from typing import ClassVar, Iterable

from texttable import Texttable

from mlib.boot.stream import arr
from mlib.obj import SimpleObject



@dataclass
class TextTableWrapper(SimpleObject):
    LEFT: ClassVar[str] = 'l'
    RIGHT: ClassVar[str] = 'r'
    CENTER: ClassVar[str] = 'c'

    TOP: ClassVar[str] = 't'
    BOTTOM: ClassVar[str] = 'b'
    MIDDLE: ClassVar[str] = 'm'

    STR: ClassVar[str] = 't'
    FLOAT: ClassVar[str] = 'f'
    EXP: ClassVar[str] = 'e'
    INT: ClassVar[str] = 'i'
    AUTO: ClassVar[str] = 'a'

    data: Iterable
    col_align: Iterable[str] = None
    col_valign: Iterable[str] = None
    col_dtype: Iterable[str] = None
    deco: int = None

    max_width: int = 80

    def __post_init__(self):
        self.data = arr(self.data)
        self._table = Texttable(max_width=self.max_width)
        self._table.add_rows(self.data)
        if self.col_align:
            self._table.set_cols_align(self.col_align)
        if self.col_valign:
            self._table.set_cols_valign(self.col_valign)
        if self.col_dtype:
            self._table.set_cols_dtype(self.col_dtype)
        if self.deco:
            self._table.set_deco(self.deco)

    def str(self):
        self._table.set_max_width(self.max_width)
        return self._table.draw()

    @staticmethod
    def example1():
        return TextTableWrapper(
            data=[["Name", "Age", "Nickname"],
                  ["Mr. Xavier Huon", 32, "Xav'"],
                  ["Mr. Baptiste Clement", 1, "Baby"],
                  ["Mme. Louise Bourgeau", 28, "Lou, Loue"]],
            col_align=[
                TextTableWrapper.LEFT,
                TextTableWrapper.RIGHT,
                TextTableWrapper.CENTER
            ],
            col_valign=[
                TextTableWrapper.TOP,
                TextTableWrapper.MIDDLE,
                TextTableWrapper.BOTTOM
            ]
        )

    @staticmethod
    def example2():
        return TextTableWrapper(
            data=[["text", "float", "exp", "int", "auto"],
                  ["abcd", "67", 654, 89, 128.001],
                  ["efghijk", 67.5434, .654, 89.6, 12800000000000000000000.00023],
                  ["lmn", 5e-78, 5e-78, 89.4, .000000000000128],
                  ["opqrstu", .023, 5e+78, 92., 12800000000000000000000]],
            col_align=[
                TextTableWrapper.LEFT,
                TextTableWrapper.RIGHT,
                TextTableWrapper.RIGHT,
                TextTableWrapper.RIGHT,
                TextTableWrapper.LEFT
            ],
            col_dtype=[
                TextTableWrapper.STR,
                TextTableWrapper.FLOAT,
                TextTableWrapper.EXP,
                TextTableWrapper.INT,
                TextTableWrapper.AUTO
            ],
            deco=Texttable.HEADER
        )
