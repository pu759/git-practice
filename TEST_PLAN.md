# 第5回 テスト計画（関数の切り出しとpytest）

- 学籍番号：2432021 
- 氏名：川村 果歩
- 提出日：2026/10/14
- 提出file名：`TEST_PLAN.md`（`~/practice` の直下に置き、commitして提出する）

> 各欄の例文や角括弧は、自分の実行結果と判断へ置き換えること。認証情報、password、tokenは記録しないこと。
> WSL2のUbuntu上で、pyenvの仮想環境を使って作業する。第4回でCopilotが生成した `~/practice/app.py` を題材にする。計算がすべて `main()` の中にある場合は、まず関数へ切り出してからtestを書く。

---

## 1. pytestの導入確認

- 使用したpyenvの仮想環境名（`pyenv version` の結果）：`practice-env`
- pytestを新たにinstallしたか：はい（新しく作成した仮想環境にインストール）
- installした場合のcommand：`python -m pip install -r requirements.txt`

```text
$ cd ~/practice
$ pyenv version
practice-env (set by PYENV_VERSION environment variable)

$ python -m pytest --version
pytest 9.1.1
```

- `requirements.txt` に `pytest` を追記したか：いいえ（最初から `pytest==9.1.1` が記載されていた）
- つまずいた点と対処（なければ「なし」）：最初は `pyenv` コマンドが認識されなかった。`~/.bashrc` にpyenvの設定を追加して解決した。その後、Python 3.14.4をpyenvでインストールし、`practice-env` を作成した。`requirements.txt` のライブラリをインストールし、pytestが正常に実行できることを確認した。

---
## 2. 切り出し前のapp.pyの構造

関数の一覧と、計算を行っている行を確認する。

```text
$ git show cdffef8:app.py | grep -n "def "
（出力なし。切り出し前のapp.pyには独立した関数定義がなかった）
```

| 行 | code（要約） | 計算 / 表示 |
|---|---|---|
| 10～17 | 画像のアップロード、RGB形式への変換、画像表示 | 入力・変換・表示 |
| 19～22 | 画像の幅・高さを表示し、NumPy配列へ変換 | 表示・データ変換 |
| 24～26 | RGB各チャンネルの平均値を計算 | 計算 |
| 28～31 | RGB平均値を小数点以下2桁で表示 | 表示 |
| 33～48 | RGBヒストグラムの作成と各チャンネルの画素数集計 | 計算・グラフ作成 |
| 50～56 | グラフの軸・タイトル・凡例を設定し、画面に表示して閉じる | 表示・後処理 |

- testから直接呼べる計算用の関数はあったか：なかった。切り出し前の `app.py` では、RGB平均値の計算やヒストグラムの作成が直接記述されており、テストから直接呼び出せる独立した計算用関数はなかった。
- 切り出し前のcommit ID：`cdffef8`（tag：`before-refactor`）

---

## 3. 関数の切り出し

### AIへ渡したprompt

```text
app.pyにまとめられている画像分析処理を、テストしやすいように関数へ切り出してください。
RGB各チャンネルの平均値を計算するmean_rgb(image)と、RGB各チャンネルのヒストグラムを作成するrgb_histograms(image)をanalysis.pyに実装してください。
app.pyからはanalysis.pyの関数を呼び出す構成にしてください。入力画像は高さ・幅・RGBの3チャンネルを持つNumPy配列を想定し、RGBの順番を維持してください。既存の画面表示とRGB平均値の計算結果が変わらないようにし、入力形式が不正な場合はValueErrorを発生させてください。
```

### AIの変更計画と人間の判断

- AIの計画（要約）：RGB平均値とRGBヒストグラムの計算処理を `analysis.py` の関数に分離し、`app.py` から呼び出す構成にする。各関数をpytestで単独テストできるようにする。
- 採用・修正した点と理由：計算処理を画面表示から分離し、`mean_rgb(image)` と `rgb_histograms(image)` を作成する方針を採用した。計算部分を個別にテストでき、不正な入力も確認できるため。ヒストグラムの描画方法は `ax.hist` から `ax.bar` に変更されたため、グラフの見た目の完全な一致までは確認していない。

### 変更内容

```text
$ git --no-pager diff cdffef8 aa09ec9 -- app.py
diff --git a/app.py b/app.py
index 494b64e..98b4204 100644
--- a/app.py
+++ b/app.py
@@ -1,9 +1,10 @@
-
 import streamlit as st
 from PIL import Image
 import numpy as np
 import matplotlib.pyplot as plt

+from analysis import mean_rgb, rgb_histograms
+
 st.title("画像分析アプリ")
 st.write("画像をアップロードして、特徴を確認するアプリです。")

@@ -21,9 +22,7 @@ if uploaded_file is not None:

     image_array = np.array(image)

-    red_mean = image_array[:, :, 0].mean()
-    green_mean = image_array[:, :, 1].mean()
-    blue_mean = image_array[:, :, 2].mean()
+    red_mean, green_mean, blue_mean = mean_rgb(image_array)

     st.subheader("RGB平均値")
     st.write(f"R（赤）の平均値：{red_mean:.2f}")
     st.write(f"G（緑）の平均値：{green_mean:.2f}")
     st.write(f"B（青）の平均値：{blue_mean:.2f}")
@@ -36,15 +35,16 @@ if uploaded_file is not None:

     colors = ["red", "green", "blue"]
     labels = ["R（赤）", "G（緑）", "B（青）"]
+    histograms = rgb_histograms(image_array)

-    for i, color in enumerate(colors):
-        ax.hist(
-            image_array[:, :, i].ravel(),
-            bins=256,
-            range=(0, 256),
+    for histogram, color, label in zip(histograms, colors, labels):
+        ax.bar(
+            np.arange(256),
+            histogram,
+            width=1.0,
             color=color,
             alpha=0.4,
-            label=labels[i]
+            label=label
         )

     ax.set_xlabel("明るさ（0～255）")
```

- 新しく作ったfileと関数：`analysis.py` に `mean_rgb(image)` と `rgb_histograms(image)` を作成した。また、`test_analysis.py` にそれらの関数を検証するテストを追加した。

### 切り出し前後の確認

同じ画像を入力し、画面に表示されるRGB平均値が変わらないことを確認する。

| 項目 | 切り出し前 | 切り出し後 |
|---|---|---|
| 使用した画像 | `sunflower.jpg`（3264 × 2448 pixel） | `sunflower.jpg`（3264 × 2448 pixel） |
| R平均 | 106.24 | 106.24 |
| G平均 | 103.41 | 103.41 |
| B平均 | 80.20 | 80.20 |

`np.allclose(old, new)` は `True` となり、RGB平均値が一致した。ヒストグラムの描画方法は変更されているため、グラフの見た目の完全な一致までは確認していない。

- 切り出し後のcommit ID：`aa09ec9`（関数分離とテストの追加）

---
## 4. 対象関数と入力契約

- 対象関数：`mean_rgb(image)`、`rgb_histograms(image)`
- 定義場所：`analysis.py`
- 入力（typeとshape）：NumPy配列（`numpy.ndarray`）、shapeは `(高さ, 幅, 3)`。高さ方向・幅方向に画素が並び、最後の次元はRGBの順番である。
- 処理：`mean_rgb(image)` は高さ方向と幅方向に平均を取り、R・G・Bそれぞれの平均画素値を計算する。`rgb_histograms(image)` はRGBそれぞれについて、画素値0～255の256ビンのヒストグラムを計算する。
- 出力（typeとshape）：`mean_rgb(image)` はR・G・Bの順に平均値を格納した3要素のNumPy配列（shape `(3,)`）を返す。`rgb_histograms(image)` はRGB各チャンネルのヒストグラムを順に格納したリストを返す。リストの各要素は256要素のNumPy配列である。
- 例外（契約違反の入力と発生させる例外）：入力配列が3次元でない場合、または最後の次元が3チャンネルでない場合は `ValueError` を発生させる。

```python
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
```
---

## 5. test case一覧

正常系2件以上、境界値2件以上、異常系1件以上。期待結果は手計算で求めた数値を書く。

| ID | 分類 | 入力 | 期待結果 | 選定理由 |
|---|---|---|---|---|
| N1 | 正常系 | 1画素 `[[[10, 20, 30]]]` | 平均値 `[10, 20, 30]` | 1画素のRGB順と基本計算を確認する |
| N2 | 正常系 | 2画素 `[[[10, 20, 30], [30, 40, 50]]]` | 平均値 `[20, 30, 40]`（各チャンネルで2画素の平均を計算） | 複数画素の平均値が正しいか確認する |
| B1 | 境界値 | 全チャンネルが0の画像 `np.zeros((2, 2, 3))` | 平均値 `[0, 0, 0]` | 画素値の最小値を確認する |
| B2 | 境界値 | 全チャンネルが255の画像 `np.full((2, 2, 3), 255)` | 平均値 `[255, 255, 255]` | 画素値の最大値を確認する |
| E1 | 異常系 | グレースケールの2次元配列 `np.zeros((2, 2))` | `ValueError` | RGBの3チャンネルを持たない入力を拒否する |
| E2 | 異常系 | 4チャンネルの配列 `np.zeros((2, 2, 4))` | `ValueError` | チャンネル数が3でない入力を拒否する |
| N3 | 正常系 | 1画素 `[[[10, 20, 30]]]` をヒストグラム関数へ入力 | Rのbin 10、Gのbin 20、Bのbin 30がそれぞれ1 | RGBの順番で画素値を数えることを確認する |
| B3 | 境界値 | `[[[0, 255, 0], [255, 0, 255]]]` | 各チャンネルのヒストグラム合計が2。Rではbin 0と255が各1 | 最小値・最大値を含む場合も全画素が数えられることを確認する |
| E3 | 異常系 | 4チャンネルの配列 `np.zeros((2, 2, 4))` をヒストグラム関数へ入力 | `ValueError` | `rgb_histograms` でも入力契約が守られることを確認する |

---

## 6. pytest実装

対象関数と同じdirectoryの `test_analysis.py` に書いたtest関数を貼る。

```python
import numpy as np
import pytest
from analysis import mean_rgb, rgb_histograms


def test_mean_rgb_one_pixel():
    image = np.array([[[10, 20, 30]]])
    assert np.allclose(mean_rgb(image), [10, 20, 30])


def test_mean_rgb_multiple_pixels():
    image = np.array([[[10, 20, 30], [30, 40, 50]]])
    assert np.allclose(mean_rgb(image), [20, 30, 40])


def test_mean_rgb_all_zeros():
    image = np.zeros((2, 2, 3), dtype=np.uint8)
    assert np.allclose(mean_rgb(image), [0, 0, 0])


def test_mean_rgb_all_255():
    image = np.full((2, 2, 3), 255, dtype=np.uint8)
    assert np.allclose(mean_rgb(image), [255, 255, 255])


def test_mean_rgb_grayscale_raises_value_error():
    image = np.zeros((2, 2), dtype=np.uint8)
    with pytest.raises(ValueError):
        mean_rgb(image)


def test_mean_rgb_four_channels_raises_value_error():
    image = np.zeros((2, 2, 4), dtype=np.uint8)
    with pytest.raises(ValueError):
        mean_rgb(image)


def test_rgb_histograms_one_pixel():
    image = np.array([[[10, 20, 30]]], dtype=np.uint8)
    histograms = rgb_histograms(image)
    assert histograms[0][10] == 1
    assert histograms[1][20] == 1
    assert histograms[2][30] == 1


def test_rgb_histograms_boundary_values_and_pixel_count():
    image = np.array([[[0, 255, 0], [255, 0, 255]]], dtype=np.uint8)
    histograms = rgb_histograms(image)
    assert all(sum(hist) == 2 for hist in histograms)
    assert histograms[0][0] == 1 and histograms[0][255] == 1


def test_rgb_histograms_four_channels_raises_value_error():
    image = np.zeros((2, 2, 4), dtype=np.uint8)
    with pytest.raises(ValueError):
        rgb_histograms(image)
```

---

## 7. pytest実行結果

最初の実行でFAILがあった場合は、その出力と対処も残す。

```text
$ python -m pytest -q
.........                                                                [100%]
9 passed in 0.07s
```

- FAILの有無と対処（例：異常系が `DID NOT RAISE` となり、入力契約の確認を追加した）：通常の最終実行ではFAILはなく、9件すべて成功した。意図的にチャンネル順を入れ替えた検証ではFAILを確認し、バグを元に戻してからテストを再実行した。

---

## 8. 意図的bugを検出した例

- 入れたbug（例：channel順を `[R, B, G]` に変更）：`mean_rgb` の戻り値のチャンネル順を `[R, B, G]` に入れ替えた。
- 失敗したtestと出力：`test_mean_rgb_one_pixel` が期待値と実際値の違いを検出した。

```text
期待値: [10, 20, 30]
実際値: [10., 30., 20.]
結果: 1 failed, 5 passed
```

- bugを戻した後の結果：`mean_rgb` の戻り値を正しいRGB順に戻した。その後、ヒストグラムのテストも追加した状態で、9件すべてのテストが成功した。以下は以前の実行結果であり、現在の仮想環境での最新結果は第7節に記載した。

```text
.........                                                                [100%]
9 passed in 0.36s
```
---

## 9. AI提案の採否

| AIが提案した内容（切り出し・test case） | 採用 / 不採用 | 理由 |
|---|---|---|
| RGB平均値の計算を `mean_rgb(image)` として切り出す | 採用 | UIと計算を分け、関数単位でテストできるため |
| ヒストグラム計算を `rgb_histograms(image)` として切り出す | 採用 | RGB各チャンネルの計算結果を個別に確認できるため |
| 全0・全255の境界値と不正な入力のテストを追加する | 採用 | 画素値の端と入力契約が正しく扱われるか確認できるため |
| チャンネル順を入れ替える意図的なバグでテストを確認する | 採用 | テストが実際に誤りを検出できることを確認できるため |

---

## 提出前の確認

- [x] `pyenv version` と `pytest --version` の結果を書いた
- [x] 切り出し前のapp.pyで、計算と表示の行を区別した（正確な行番号は記録なし）
- [x] 切り出しのpromptと `git diff` を貼った（diff全文ではなく、変更内容の要約であることを明記）
- [x] 切り出し前後で同じ画像のRGB平均値が一致することを確認した
- [x] 対象関数の入力契約（type・shape・例外）を書いた
- [x] 正常系2件・境界値2件・異常系1件以上を表にし、期待結果を手計算で示した
- [x] pytestの実装と実行結果を貼った
- [x] 意図的bugで失敗する様子と戻した結果を貼った
- [x] AI提案の採否と理由を書いた
- [x] `~/practice` 直下に `TEST_PLAN.md` として保存し、commitした
