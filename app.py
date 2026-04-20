
import streamlit as st
import tempfile
import cv2

from main import analyze


st.title("β-gal Cell Analyzer")

uploaded_file = st.file_uploader("画像をアップロード", type=["png", "jpg", "jpeg", "tif"])

if uploaded_file is not None:

    # 一時保存
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(uploaded_file.read())

    st.write("解析中...")

    result = analyze(tfile.name)

    st.subheader("結果")

    st.write(f"Total cells: {result['total']}")
    st.write(f"Positive cells: {result['positive']}")
    st.write(f"Ratio: {result['ratio']*100:.1f}%")

    # 画像表示
    img = cv2.imread(result["output_image"])
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    st.image(img, caption="解析結果", use_container_width=True)
