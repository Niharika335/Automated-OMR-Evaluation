import streamlit as st
import requests

st.title("Automated OMR Evaluation")

# Step 1: Upload Excel Answer Key
st.header("Step 1: Upload Answer Key (Excel with multiple sheets)")
key_file = st.file_uploader("Upload Excel file", type=["xlsx"])
available_sets = []

if key_file:
    res = requests.post(
        "http://127.0.0.1:8000/upload-answer-key",
        files={"file": key_file.getvalue()}
    )
    res_json = res.json()
    st.success(res_json)
    if "sets" in res_json:
        available_sets = res_json["sets"]

# Step 2: Upload OMR Sheets
st.header("Step 2: Upload OMR Sheets")
uploaded_files = st.file_uploader(
    "Upload multiple OMR sheets", 
    type=["jpg","png","pdf"], 
    accept_multiple_files=True
)

set_name = None
if available_sets:
    set_name = st.selectbox("Select Set", available_sets)

if uploaded_files and set_name:
    if st.button("Submit Sheets"):
        files = [("files", (f.name, f.getvalue(), f.type)) for f in uploaded_files]
        res = requests.post(
            "http://127.0.0.1:8000/upload-omr",
            files=files,
            data={"set_name": set_name}
        )
        st.json(res.json())
