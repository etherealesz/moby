import cv2
import numpy as np

from core.config.settings import settings


class ImagePreprocessor:
    def __init__(
        self,
        clip_limit: float | None = None,
        tile_grid_size: tuple[int, int] | None = None,
    ) -> None:
        clahe_config = settings.classification.clahe
        self._clip_limit = (
            clip_limit if clip_limit is not None else clahe_config.clip_limit
        )
        self._tile_grid_size = (
            tuple(tile_grid_size)
            if tile_grid_size is not None
            else tuple(clahe_config.tile_grid_size)
        )
        self._clahe = cv2.createCLAHE(
            clipLimit=self._clip_limit,
            tileGridSize=self._tile_grid_size,
        )

    @property
    def clip_limit(self) -> float:
        return self._clip_limit

    @property
    def tile_grid_size(self) -> tuple[int, int]:
        return self._tile_grid_size

    def rgb_to_lab(self, img: np.ndarray) -> np.ndarray:
        return cv2.cvtColor(img, cv2.COLOR_RGB2LAB)

    def apply_clahe(self, lightness: np.ndarray) -> np.ndarray:
        return self._clahe.apply(lightness)

    def lab_to_rgb(self, lab: np.ndarray) -> np.ndarray:
        return cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)

    def process(self, frame: np.ndarray) -> np.ndarray:
        if frame.dtype != np.uint8 or frame.ndim != 3 or frame.shape[2] != 3:
            raise ValueError("frame must be an RGB uint8 array with shape (H, W, 3)")

        lab = self.rgb_to_lab(frame)
        lightness, a_channel, b_channel = cv2.split(lab)
        enhanced_lab = cv2.merge((self.apply_clahe(lightness), a_channel, b_channel))
        return self.lab_to_rgb(enhanced_lab)
