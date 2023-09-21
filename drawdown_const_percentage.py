from typing import List
from drawdown import Drawdown


class DrawdownConstPercentage(Drawdown):
    def __init__(self, percentage):
        super().__init__()
        self._percentage = percentage



