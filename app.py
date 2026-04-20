
import streamlit as st
import tempfile
from PIL import Image

from main import analyze


st.title("β-gal Cell Analyzer")

uploaded_file = st.file_uploader(
    "画像をアップロード",
    type=["png", "jpg", "jpeg", "tif"]
)

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

    # 👇 cv2使わない（超重要）
    image = Image.open(result["output_image"])
    st.image(image, caption="解析結果", use_container_width=True)

