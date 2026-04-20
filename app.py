import streamlit as st
import numpy as np
import cv2
from pathlib import Path
import tempfile

from analysis import analyze  # ← あなたの関数をimport


st.title("β-gal Cell Analyzer")

uploaded_file = st.file_uploader("画像をアップロード", type=["png", "jpg", "tif"])

if uploaded_file is not None:

    # 一時保存
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(uploaded_file.read())

    st.write("解析中...")

    analyze(tfile.name)

    # 結果画像表示
    result_path = Path(tfile.name).with_name("result_overlay.png")

    if result_path.exists():
        img = cv2.imread(str(result_path))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        st.image(img, caption="解析結果", use_column_width=True)

