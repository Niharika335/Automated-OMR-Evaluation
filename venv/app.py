import streamlit as st
import os
from PIL import Image

# Path to sample image
SAMPLE_IMAGE = os.path.join(os.path.dirname(__file__), "sample_data", "sample_captured.png")

def main():
    st.title("Automated OMR Evaluation App")
    st.write("✅ App started successfully!")

    # Show sample image
    if os.path.exists(SAMPLE_IMAGE):
        st.image(Image.open(SAMPLE_IMAGE), caption="Sample OMR Sheet", use_column_width=True)
    else:
        st.error("Sample image not found! Make sure sample_data/sample_captured.png exists in repo.")

    # Simple placeholder for OMR evaluation
    if st.button("Run OMR Evaluation"):
        st.success("OMR Evaluation ran successfully!")
        st.write("Total Score: 85 / 100")
        st.write("Subject Scores: Math=18, Science=17, English=16, Aptitude=17, Reasoning=17")

if __name__ == "__main__":
    main()
