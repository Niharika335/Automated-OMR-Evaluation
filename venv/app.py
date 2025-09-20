# app.py
import streamlit as st
import pandas as pd
import os
from template_generator import main as gen_main
from omr import process_image

st.set_page_config(page_title="OMR Auto-evaluator", layout="wide")

st.title("Automated OMR Evaluation — Demo (Theme 1)")

# Ensure sample data exists
if not os.path.exists("sample_data/sample_captured.png"):
    st.info("Generating sample template and sample captured image for demo...")
    gen_main()

st.sidebar.header("Demo options")
use_sample = st.sidebar.checkbox("Use generated sample image", value=True)

uploaded_file = None
if use_sample:
    sample_path = "sample_data/sample_captured.png"
    st.sidebar.write("Using sample image created by `template_generator.py`")
    uploaded_file = sample_path
else:
    uploaded = st.sidebar.file_uploader("Upload OMR image (png/jpg)", type=["png","jpg","jpeg"])
    if uploaded is not None:
        # save uploaded file
        path = os.path.join("sample_data", "uploaded.png")
        with open(path, "wb") as f:
            f.write(uploaded.getbuffer())
        uploaded_file = path

if uploaded_file:
    st.subheader("Input image")
    st.image(uploaded_file, use_column_width=True)

    if st.button("Run OMR Evaluation"):
        try:
            result = process_image(uploaded_file)
            score = result["score"]
            st.success(f"Total Score: {score['total']} / 100")
            for i, s in enumerate(score["per_subject"], start=1):
                st.write(f"Subject {i}: {s} / 20")
            # show overlay
            st.subheader("Detected overlay (green=correct, red=wrong)")
            st.image(result["overlay_path"], use_column_width=True)

            # produce CSV
            rows = []
            for q in range(len(score["selected"])):
                rows.append({
                    "Question": q+1,
                    "Selected": score["selected"][q],
                    "Correct": "Yes" if score["correct_mask"][q] else "No"
                })
            df = pd.DataFrame(rows)
            st.dataframe(df)

            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("Download per-question CSV", data=csv, file_name="omr_results.csv", mime="text/csv")
        except Exception as e:
            st.error(f"Error: {e}")
            st.stop()

st.markdown("---")
st.markdown("**How to use:** Click `Run OMR Evaluation` to process the sample (or your uploaded) image.")
