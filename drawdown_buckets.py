from typing import List
from drawdown import Drawdown


class DrawdownBuckets(Drawdown):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self._bucket1 = kwargs['bucket1']
        self._bucket2 = kwargs['bucket2']
        self._bucket3 = kwargs['bucket3']





