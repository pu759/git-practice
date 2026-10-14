import numpy as np


def mean_rgb(image):
    """RGB画像の各チャンネルの平均値を返す。"""
    if image.ndim != 3 or image.shape[2] != 3:
        raise ValueError("RGB image [H,W,3] required")

    return image.mean(axis=(0, 1))


def rgb_histograms(image):
    """RGB画像の各チャンネルのヒストグラムを返す。"""
    if image.ndim != 3 or image.shape[2] != 3:
        raise ValueError("RGB image [H,W,3] required")

    histograms = []

    for i in range(3):
        histogram, _ = np.histogram(
            image[:, :, i],
            bins=256,
            range=(0, 256)
        )
        histograms.append(histogram)

    return histograms
