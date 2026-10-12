from typing import NamedTuple

import numpy as np


class DClassification(NamedTuple):
    probabilities: np.ndarray
    label: str
