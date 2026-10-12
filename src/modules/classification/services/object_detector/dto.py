from typing import NamedTuple


class DBox(NamedTuple):
    x1: float
    y1: float
    x2: float
    y2: float
    confidence: float
