import streamlit as st
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

from analysis import mean_rgb, rgb_histograms

st.title("画像分析アプリ")
st.write("画像をアップロードして、特徴を確認するアプリです。")

uploaded_file = st.file_uploader(
    "画像を選択してください",
    type=["png", "jpg", "jpeg"]
)

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="アップロードした画像")

    st.write(f"画像の幅：{image.width} ピクセル")
    st.write(f"画像の高さ：{image.height} ピクセル")

    image_array = np.array(image)

    red_mean, green_mean, blue_mean = mean_rgb(image_array)

    st.subheader("RGB平均値")
    st.write(f"R（赤）の平均値：{red_mean:.2f}")
    st.write(f"G（緑）の平均値：{green_mean:.2f}")
    st.write(f"B（青）の平均値：{blue_mean:.2f}")

    st.subheader("RGBヒストグラム")

    fig, ax = plt.subplots()

    colors = ["red", "green", "blue"]
    labels = ["R（赤）", "G（緑）", "B（青）"]
    histograms = rgb_histograms(image_array)

    for histogram, color, label in zip(histograms, colors, labels):
        ax.bar(
            np.arange(256),
            histogram,
            width=1.0,
            color=color,
            alpha=0.4,
            label=label
        )

    ax.set_xlabel("明るさ（0～255）")
    ax.set_ylabel("画素数")
    ax.set_title("RGBの色の分布")
    ax.legend()

    st.pyplot(fig)
    plt.close(fig)
