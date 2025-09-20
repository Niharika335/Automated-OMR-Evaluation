from fastapi import FastAPI, UploadFile, File, Form
import pandas as pd

app = FastAPI()

ANSWER_KEYS = {}  # global dictionary: {SetName: {Q.No: Answer}}

@app.post("/upload-answer-key")
async def upload_answer_key(file: UploadFile = File(...)):
    global ANSWER_KEYS
    # Read all sheets
    xls = pd.ExcelFile(file.file)
    keys = {}

    for sheet_name in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet_name)

        # Expecting columns: Q.No, Subject, Answer
        keys[sheet_name] = {
            int(row["Q.No"]): str(row["Answer"]).strip()
            for _, row in df.iterrows()
        }

    ANSWER_KEYS = keys
    return {"status": "Answer keys uploaded", "sets": list(keys.keys())}


@app.post("/upload-omr")
async def upload_omr(files: list[UploadFile] = File(...), set_name: str = Form(...)):
    if not ANSWER_KEYS:
        return {"error": "Upload answer keys first!"}
    if set_name not in ANSWER_KEYS:
        return {"error": f"Set {set_name} not found in uploaded answer keys"}

    results = []
    for file in files:
        # TODO: call omr_core.evaluate_omr(file)
        # placeholder: score by length of key
        score = len(ANSWER_KEYS[set_name])
        results.append({"student": file.filename, "set": set_name, "score": score})
    return {"results": results}
