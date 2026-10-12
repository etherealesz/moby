import cv2
import numpy as np
import timm
import torch
from torch import nn

from core.constants.waste import WASTE_CATEGORY_LABELS

MODEL_NAME = "mobilenetv4_conv_small.e2400_r224_in1k"


def build_waste_classifier_model(pretrained: bool) -> nn.Module:
    return timm.create_model(
        MODEL_NAME,
        pretrained=pretrained,
        num_classes=len(WASTE_CATEGORY_LABELS),
    )


def get_normalization(model: nn.Module) -> tuple[tuple[float, ...], tuple[float, ...]]:
    data_config = timm.data.resolve_model_data_config(model)
    return tuple(data_config["mean"]), tuple(data_config["std"])


def preprocess_crops(
    crops: list[np.ndarray],
    image_size: int,
    mean: tuple[float, ...],
    std: tuple[float, ...],
) -> torch.Tensor:
    mean_array = np.asarray(mean, dtype=np.float32)
    std_array = np.asarray(std, dtype=np.float32)
    batch = np.stack(
        [
            (
                cv2.resize(
                    crop, (image_size, image_size), interpolation=cv2.INTER_LINEAR
                ).astype(np.float32)
                / 255.0
                - mean_array
            )
            / std_array
            for crop in crops
        ]
    )
    return torch.from_numpy(batch.transpose(0, 3, 1, 2).copy())
