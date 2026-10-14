import numpy as np
import pytest

from analysis import mean_rgb, rgb_histograms


def test_mean_rgb_one_pixel():
    image = np.array([[[10, 20, 30]]])

    result = mean_rgb(image)

    np.testing.assert_allclose(result, [10, 20, 30])


def test_mean_rgb_multiple_pixels():
    image = np.array([
        [[0, 10, 20], [100, 110, 120]],
        [[200, 210, 220], [100, 70, 40]]
    ])

    result = mean_rgb(image)

    np.testing.assert_allclose(result, [100, 100, 100])


def test_mean_rgb_all_zeros():
    image = np.zeros((2, 2, 3), dtype=np.uint8)

    result = mean_rgb(image)

    np.testing.assert_allclose(result, [0, 0, 0])


def test_mean_rgb_all_255():
    image = np.full((2, 2, 3), 255, dtype=np.uint8)

    result = mean_rgb(image)

    np.testing.assert_allclose(result, [255, 255, 255])


def test_mean_rgb_grayscale_raises_error():
    image = np.array([[0, 100], [150, 255]])

    with pytest.raises(ValueError):
        mean_rgb(image)


def test_rgb_histograms_one_pixel():
    image = np.array([[[10, 20, 30]]])

    result = rgb_histograms(image)

    assert len(result) == 3
    assert all(len(histogram) == 256 for histogram in result)
    assert result[0][10] == 1
    assert result[1][20] == 1
    assert result[2][30] == 1
