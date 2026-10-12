import numpy as np

M_RGB_TO_XYZ = np.array(
    [
        [0.412453, 0.357580, 0.180423],
        [0.212671, 0.715160, 0.072169],
        [0.019334, 0.119193, 0.950227],
    ]
)
M_XYZ_TO_RGB = np.linalg.inv(M_RGB_TO_XYZ)

WHITE_POINT = np.array([0.950456, 1.0, 1.088754])

DELTA = 6.0 / 29.0


def srgb_to_linear(c: np.ndarray) -> np.ndarray:
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def linear_to_srgb(c: np.ndarray) -> np.ndarray:
    c = np.clip(c, 0.0, 1.0)
    return np.where(c <= 0.0031308, 12.92 * c, 1.055 * c ** (1 / 2.4) - 0.055)


def f(t: np.ndarray) -> np.ndarray:
    return np.where(t > DELTA**3, np.cbrt(t), t / (3 * DELTA**2) + 4.0 / 29.0)


def f_inverse(t: np.ndarray) -> np.ndarray:
    return np.where(t > DELTA, t**3, 3 * DELTA**2 * (t - 4.0 / 29.0))


def rgb_to_lab(rgb_uint8: np.ndarray) -> np.ndarray:
    linear = srgb_to_linear(rgb_uint8.astype(np.float64) / 255.0)
    xyz = linear @ M_RGB_TO_XYZ.T
    fx, fy, fz = np.moveaxis(f(xyz / WHITE_POINT), -1, 0)
    lightness = 116.0 * fy - 16.0
    a = 500.0 * (fx - fy)
    b = 200.0 * (fy - fz)
    return np.stack([lightness, a, b], axis=-1)


def lab_to_rgb(lab: np.ndarray) -> np.ndarray:
    lightness, a, b = np.moveaxis(lab, -1, 0)
    fy = (lightness + 16.0) / 116.0
    fx = fy + a / 500.0
    fz = fy - b / 200.0
    xyz = np.stack([f_inverse(fx), f_inverse(fy), f_inverse(fz)], axis=-1) * WHITE_POINT
    linear = xyz @ M_XYZ_TO_RGB.T
    return np.clip(np.round(linear_to_srgb(linear) * 255.0), 0, 255).astype(np.uint8)


def lab_to_opencv_8bit(lab: np.ndarray) -> np.ndarray:
    scaled = np.stack(
        [lab[..., 0] * 255.0 / 100.0, lab[..., 1] + 128.0, lab[..., 2] + 128.0], axis=-1
    )
    return np.clip(np.round(scaled), 0, 255).astype(np.uint8)


def opencv_8bit_to_lab(lab_uint8: np.ndarray) -> np.ndarray:
    lab = lab_uint8.astype(np.float64)
    return np.stack(
        [lab[..., 0] * 100.0 / 255.0, lab[..., 1] - 128.0, lab[..., 2] - 128.0], axis=-1
    )
