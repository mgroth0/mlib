from typing import Optional

from mlib.fig.PlotData import FigData


class TableData(FigData):
    def __init__(self,
                 data,
                 row_headers=None,
                 col_headers=None,
                 top_header_label=None,
                 side_header_label=None,
                 **kwargs):
        super(TableData, self).__init__(**kwargs)
        self.data = data
        self.item_type = 'table'
        self.confuse = False
        self.confuse_max = None
        self.confuse_target = None
        self.confuse_is_identical = False
        self.row_headers = row_headers
        self.col_headers = col_headers
        self.top_header_label = top_header_label
        self.side_header_label = side_header_label

class ConfusionMatrix(TableData):
    def __init__(self,
                 data,
                 confuse_max,
                 confuse_target,
                 headers_included,
                 show_nums=True,
                 top_header_label: Optional[str] = "Prediction",
                 side_header_label: Optional[str] = "True",
                 block_len=None,
                 confuse_is_identical=False,
                 *args, **kwargs):
        super(ConfusionMatrix, self).__init__(
            *args,
            data=data,
            top_header_label=top_header_label,
            side_header_label=side_header_label,
            **kwargs)
        self.confuse = True
        self.confuse_max = confuse_max
        self.confuse_target = confuse_target
        self.confuse_is_identical = confuse_is_identical
        self.block_len = block_len
        self.show_nums = show_nums
        self.headers_included = headers_included

class RSAMatrix(ConfusionMatrix):
    def __init__(
            self,
            *args,
            **kwargs
    ):
        super(RSAMatrix, self).__init__(
            *args,
            top_header_label=None,
            side_header_label=None,
            confuse_is_identical=True,
            headers_included=False,
            show_nums=False,
            **kwargs
        )
