import threading
from pathlib import Path

import numpy as np
import torch

from core.config.settings import settings
from core.constants.paths import PROJECT_ROOT
from core.constants.waste import WASTE_CATEGORY_LABELS
from core.logger.factory import create_app_logger
from core.utils.device_helper import resolve_torch_device
from modules.classification.exceptions.classification import (
    ClassifierLabelMismatchError,
    ClassifierModelNotAvailableError,
)
from modules.classification.services.waste_classifier.dto import DClassification
from modules.classification.services.waste_classifier.utils import (
    build_waste_classifier_model,
    preprocess_crops,
)

logger = create_app_logger()


class WasteClassifier:
    def __init__(self, weights_path: str | Path | None = None) -> None:
        classifier_config = settings.classification.classifier
        path = Path(weights_path or classifier_config.weights_path)
        self._weights_path = path if path.is_absolute() else PROJECT_ROOT / path
        self._image_size = classifier_config.image_size
        self._device = torch.device(resolve_torch_device(settings.classification.device))
        self._model: torch.nn.Module | None = None
        self._mean: tuple[float, ...] = ()
        self._std: tuple[float, ...] = ()
        self._lock = threading.Lock()

    def _load_model(self) -> torch.nn.Module:
        if self._model is not None:
            return self._model

        if not self._weights_path.exists():
            logger.error(f"Classifier weights not found: {self._weights_path}")
            raise ClassifierModelNotAvailableError

        logger.info(f"Loading classifier weights from {self._weights_path}")
        checkpoint = torch.load(
            self._weights_path, map_location="cpu", weights_only=False
        )
        if tuple(checkpoint["labels"]) != WASTE_CATEGORY_LABELS:
            raise ClassifierLabelMismatchError

        model = build_waste_classifier_model(pretrained=False)
        model.load_state_dict(checkpoint["state_dict"])
        model.eval().to(self._device)

        self._image_size = int(checkpoint.get("image_size", self._image_size))
        self._mean = tuple(checkpoint["mean"])
        self._std = tuple(checkpoint["std"])
        self._model = model
        return model

    def load_model(self, model: torch.nn.Module, mean, std) -> None:
        self._model = model.eval().to(self._device)
        self._mean = tuple(mean)
        self._std = tuple(std)

    @torch.inference_mode()
    def predict(self, crops: list[np.ndarray]) -> list[DClassification]:
        if not crops:
            return []

        with self._lock:
            model = self._load_model()
            batch = preprocess_crops(crops, self._image_size, self._mean, self._std)
            logits = model(batch.to(self._device))
            probabilities = torch.softmax(logits.float(), dim=1).cpu().numpy()

        return [
            DClassification(
                probabilities=probs,
                label=WASTE_CATEGORY_LABELS[int(np.argmax(probs))],
            )
            for probs in probabilities
        ]
