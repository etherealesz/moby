import numpy as np
import pytest
import torch

from core.constants.waste import WASTE_CATEGORY_LABELS
from modules.classification.exceptions.classification import (
    ClassifierLabelMismatchError,
    ClassifierModelNotAvailableError,
)
from modules.classification.services.waste_classifier.service import WasteClassifier
from modules.classification.services.waste_classifier.utils import (
    build_waste_classifier_model,
    get_normalization,
    preprocess_crops,
)


@pytest.fixture(scope="module")
def model() -> torch.nn.Module:
    return build_waste_classifier_model(pretrained=False)


def test_model_has_four_output_classes(model: torch.nn.Module):
    with torch.inference_mode():
        logits = model.eval()(torch.zeros(2, 3, 224, 224))
    assert logits.shape == (2, len(WASTE_CATEGORY_LABELS))


def test_preprocess_crops_resizes_and_normalizes(model: torch.nn.Module):
    mean, std = get_normalization(model)
    crops = [
        np.full((50, 80, 3), 255, dtype=np.uint8),
        np.zeros((300, 120, 3), dtype=np.uint8),
    ]
    batch = preprocess_crops(crops, 224, mean, std)

    assert batch.shape == (2, 3, 224, 224)
    assert batch[0, 0, 0, 0].item() == pytest.approx((1.0 - mean[0]) / std[0], rel=1e-5)
    assert batch[1, 2, 0, 0].item() == pytest.approx((0.0 - mean[2]) / std[2], rel=1e-5)


def test_predict_returns_softmax_probabilities(model: torch.nn.Module):
    classifier = WasteClassifier()
    classifier.load_model(model, *get_normalization(model))
    rng = np.random.default_rng(0)
    crops = [rng.integers(0, 256, size=(64, 48, 3), dtype=np.uint8) for _ in range(3)]

    results = classifier.predict(crops)

    assert len(results) == 3
    for result in results:
        assert result.probabilities.shape == (4,)
        assert result.probabilities.sum() == pytest.approx(1.0, abs=1e-5)
        assert result.label == WASTE_CATEGORY_LABELS[int(np.argmax(result.probabilities))]
    assert classifier.predict([]) == []


def test_load_checkpoint_from_file(tmp_path, model: torch.nn.Module):
    mean, std = get_normalization(model)
    weights = tmp_path / "best.pt"
    torch.save(
        {
            "state_dict": model.state_dict(),
            "labels": list(WASTE_CATEGORY_LABELS),
            "image_size": 224,
            "mean": mean,
            "std": std,
        },
        weights,
    )

    results = WasteClassifier(weights_path=weights).predict(
        [np.zeros((32, 32, 3), dtype=np.uint8)]
    )
    assert results[0].probabilities.sum() == pytest.approx(1.0, abs=1e-5)


def test_checkpoint_with_wrong_label_order_is_rejected(tmp_path, model: torch.nn.Module):
    mean, std = get_normalization(model)
    weights = tmp_path / "wrong.pt"
    torch.save(
        {
            "state_dict": model.state_dict(),
            "labels": ["B3", "Anorganik", "Organik", "Residu"],
            "mean": mean,
            "std": std,
        },
        weights,
    )

    with pytest.raises(ClassifierLabelMismatchError):
        WasteClassifier(weights_path=weights).predict(
            [np.zeros((8, 8, 3), dtype=np.uint8)]
        )


def test_missing_weights_raise(tmp_path):
    with pytest.raises(ClassifierModelNotAvailableError):
        WasteClassifier(weights_path=tmp_path / "none.pt").predict(
            [np.zeros((8, 8, 3), dtype=np.uint8)]
        )
