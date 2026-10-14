# テスト計画書（TEST_PLAN.md）

## 1. テスト環境

### 1.1 使用環境

| 項目         | 内容                     |
| ---------- | ---------------------- |
| OS         | Ubuntu（WSL環境）          |
| Python     | 3.14.4                 |
| pytest     | 9.1.1                  |
| Streamlit  | 1.65.0                 |
| Pillow     | 12.3.0                 |
| NumPy      | 2.5.4                  |
| Matplotlib | 3.11.2                 |
| 仮想環境       | `/home/kaho/venvs/dla` |

### 1.2 pytestの導入状況

pytestがインストールされていることを確認し、`python -m pytest --version` でバージョン9.1.1と表示された。また、テストを実行できることも確認した。

### 1.3 requirements.txt

プロジェクトで使用するライブラリとバージョンを管理するため、`requirements.txt` を作成した。Streamlit、Pillow、NumPy、Matplotlib、pytestの5つを記載した。

なお、今回の環境では `pyenv` コマンドが見つからなかった。そのため、Pythonのバージョン管理については未設定の課題として残っている。実際に使用したPythonは3.14.4である。

## 2. リファクタリング前の構造

### 2.1 リファクタリング前のコミット

`cdffef8`（Add image analysis Streamlit app）

### 2.2 app.pyの構造

リファクタリング前の `app.py` では、画像のアップロード、RGB形式への変換、画像の表示、画像の幅と高さの表示、NumPy配列への変換、RGB平均値の計算、RGBヒストグラムの作成を1つのファイルで行っていた。

`def` で定義された関数はなく、計算処理と画面表示の処理が同じファイル内にまとめられていた。

### 2.3 分離する処理

* **計算処理：** RGB各チャンネルの平均値の計算、RGB各チャンネルのヒストグラムの計算
* **表示処理：** 画像のアップロード、画像の表示、幅と高さの表示、計算結果の表示、ヒストグラムの描画

計算処理を別ファイルに分離することで、処理の再利用と単体テストを行いやすくすることを目的とした。

## 3. リファクタリングの実施内容

### 3.1 AIへの依頼と計画

GitHub Copilot CLIを使用し、既存の `app.py` の構造を確認して、計算処理と画面表示の処理を分離する計画を検討した。また、変更前後のコミットや差分を確認し、追加したテストが必要なケースを満たしているかを検討した。

※以下は作業内容の要約であり、AIとの会話を逐語的に再現したものではない。

### 3.2 人間による判断

計算処理を `analysis.py` に分離し、`app.py` から呼び出す構成を採用した。また、RGB平均値だけでなく、ヒストグラムの計算も関数に分離した。

AIの提案をそのまま受け入れるのではなく、コードの差分とテスト結果を確認する方針とした。

### 3.3 変更したファイルと関数

| ファイル               | 変更内容                                |
| ------------------ | ----------------------------------- |
| `app.py`           | 計算処理を `analysis.py` の関数に置き換えた       |
| `analysis.py`      | `mean_rgb` と `rgb_histograms` を定義した |
| `test_analysis.py` | 各関数の正常系、境界値、異常系をテストした               |
| `requirements.txt` | 使用ライブラリとバージョンを記録した                  |

### 3.4 コミット

* リファクタリング前：`cdffef8`
* リファクタリング後：`aa09ec9`

### 3.5 変更前後のRGB平均値の比較

リファクタリング後のアプリでは、画像サイズが3264×2448ピクセルの画像について、RGB平均値がR＝106.24、G＝103.41、B＝80.20と表示された。

ただし、リファクタリング前に同じ画像で取得したRGB平均値の記録がないため、変更前後の数値が一致することは確認できていない。今後、同じ画像を使用して両方のバージョンを実行し、結果を比較する必要がある。

また、ヒストグラムの描画方法は、変更前の `ax.hist` から変更後の `ax.bar` に変わっている。そのため、ヒストグラムの画面表示が完全に同じであるかについても、別途確認が必要である。

## 4. 対象関数の仕様

### 4.1 mean_rgb(image)

**入力**

* NumPy配列
* 形状は `[H, W, 3]`
* Hは画像の高さ、Wは画像の幅、3はRGBの各チャンネルを表す

**処理**

高さ方向と幅方向に対して平均値を計算し、R、G、Bそれぞれの平均値を求める。

**出力**

3つの値を持つNumPy配列。順番はR、G、Bである。

**例外**

入力が3次元配列でない場合、またはチャンネル数が3でない場合は `ValueError` を発生させる。

**関数定義**

```python
def mean_rgb(image):
    """RGB画像の各チャンネルの平均値を返す。"""
    if image.ndim != 3 or image.shape[2] != 3:
        raise ValueError("RGB image [H,W,3] required")
    return image.mean(axis=(0, 1))
```

### 4.2 rgb_histograms(image)

**入力**

* NumPy配列
* 形状は `[H, W, 3]`

**処理**

R、G、Bの各チャンネルについて、明るさ0～255の範囲を256個のビンに分け、各明るさの画素数を数える。

**出力**

R、G、Bの順に並んだ3つのヒストグラムのリスト。それぞれのヒストグラムは256個の要素を持つNumPy配列である。

**例外**

入力が3次元配列でない場合、またはチャンネル数が3でない場合は `ValueError` を発生させる。

**関数定義**

```python
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
```

## 5. テストケース

### 5.1 mean_rgbのテスト

| ID | 分類  | 入力                 | 期待結果              |
| -- | --- | ------------------ | ----------------- |
| N1 | 正常系 | 1画素 `[10, 20, 30]` | `[10, 20, 30]`    |
| N2 | 正常系 | 4画素のRGB値を使用        | `[100, 100, 100]` |
| B1 | 境界値 | すべて0の画像            | `[0, 0, 0]`       |
| B2 | 境界値 | すべて255の画像          | `[255, 255, 255]` |
| E1 | 異常系 | 2次元のグレースケール画像      | `ValueError`      |
| E2 | 異常系 | チャンネル数が4の画像        | `ValueError`      |

N2では、次の4画素を使用する。

```python
[
    [[0, 10, 20], [100, 110, 120]],
    [[200, 210, 220], [100, 70, 40]]
]
```

Rの平均値は `(0 + 100 + 200 + 100) / 4 = 100`、Gの平均値は `(10 + 110 + 210 + 70) / 4 = 100`、Bの平均値は `(20 + 120 + 220 + 40) / 4 = 100` となる。

### 5.2 rgb_histogramsのテスト

| ID | 分類  | 入力                         | 期待結果                        |
| -- | --- | -------------------------- | --------------------------- |
| N3 | 正常系 | 1画素 `[10, 20, 30]`         | 各チャンネルの対応するビンが1             |
| B3 | 境界値 | RGB値に0、1、253、254、255を含む4画素 | 各ヒストグラムの合計が4、0と255のビンがそれぞれ1 |
| E3 | 異常系 | チャンネル数が4の画像                | `ValueError`                |

ヒストグラムは、画素数が正しく数えられていること、配列の長さが256であること、RGBの順番が正しいことを確認する。

## 6. テストコード

実際のテストコードは `test_analysis.py` に記載した。以下はその内容である。

```python
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


def test_rgb_histograms_include_boundaries_and_count_all_pixels():
    image = np.array([
        [[0, 255, 0], [255, 0, 255]],
        [[1, 254, 2], [254, 1, 253]]
    ], dtype=np.uint8)

    histograms = rgb_histograms(image)

    assert len(histograms) == 3
    for histogram in histograms:
        assert histogram.sum() == 4

    for histogram in histograms:
        assert histogram[0] == 1
        assert histogram[255] == 1


def test_rgb_histograms_invalid_channel_count_raises_error():
    image = np.zeros((2, 2, 4), dtype=np.uint8)
    with pytest.raises(ValueError):
        rgb_histograms(image)


def test_mean_rgb_invalid_channel_count_raises_error():
    image = np.zeros((2, 2, 4), dtype=np.uint8)
    with pytest.raises(ValueError):
        mean_rgb(image)
```

## 7. テスト実行結果

### 7.1 最終的なテスト結果

`python -m pytest -v` を実行し、9件すべてが成功した。

```text
platform linux -- Python 3.14.4, pytest-9.1.1
collected 9 items
all 9 tests PASSED
=========================== 9 passed in 0.31s ===========================
```

### 7.2 結果の考察

RGB平均値について、1画素の画像、複数画素の画像、すべて0の画像、すべて255の画像で期待値と一致した。また、グレースケール画像や4チャンネル画像を入力した場合に、想定どおり例外が発生することを確認した。

ヒストグラムについても、3チャンネル分のデータが返ること、各ヒストグラムの長さが256であること、画素数が正しく集計されることを確認した。

## 8. 意図的なバグの検出

### 8.1 バグの内容

RGB平均値を返す順番を意図的に変更し、GとBの値が入れ替わるようにした。

変更した処理は次のとおりである。

```python
return image.mean(axis=(0, 1))[[0, 2, 1]]
```

本来はR、G、Bの順に返すべきところ、R、B、Gの順になってしまうバグである。

### 8.2 バグを入れたときの結果

テストを実行したところ、`test_mean_rgb_one_pixel` が失敗した。入力値は `[10, 20, 30]` であり、期待値は `[10, 20, 30]` だったが、実際の結果は `[10., 30., 20.]` となった。

```text
FAIL test_mean_rgb_one_pixel
actual:   [10., 30., 20.]
desired:  [10, 20, 30]

1 failed, 5 passed in 0.16s
```

この結果から、テストによってRGBの順番が入れ替わるバグを検出できたことが分かる。

### 8.3 バグを修正した後の結果

変更した処理を元の状態に戻し、再度テストを実行した。その結果、当時の6件のテストはすべて成功した。

```text
6 passed in 0.14s
```

その後、ヒストグラムの境界値と画素数、4チャンネル画像のエラーに関するテストを追加し、最終的に9件すべてが成功した。

## 9. AIの提案に対する判断

GitHub Copilot CLIを利用し、コードの構造確認、関数の分離方針、テストケースの不足について検討した。

追加提案のうち、ヒストグラムの境界値と画素数を確認するテスト、および4チャンネル画像で例外が発生することを確認するテストを採用した。これにより、正常な入力だけでなく、境界値や不正な入力も確認できるようになった。

一方、AIの説明だけで処理が正しいと判断せず、実際にpytestを実行して結果を確認した。最終的には9件すべてのテストが成功した。

また、リファクタリング前後で同じ画像を使ったRGB平均値の比較や、ヒストグラムの画面表示の比較は完了していない。これらは今後の確認課題として残す。

## 10. まとめ

今回の作業では、画像分析アプリの計算処理を `analysis.py` に分離し、RGB平均値とヒストグラムの計算を個別にテストできるようにした。

正常系、境界値、異常系を含む9件のテストを作成し、すべて成功した。また、RGBの順番を入れ替える意図的なバグをテストで検出し、修正後に再び成功することを確認した。

今後は、リファクタリング前後で同じ画像を使用した数値比較と、ヒストグラムの表示結果の比較を行い、計算結果だけでなく画面表示も含めて動作を確認する必要がある。
