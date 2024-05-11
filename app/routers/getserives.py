from fastapi import FastAPI, UploadFile, File
import pandas as pd
import os

app = FastAPI()


ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024 
EXPECTED_COLUMNS = ['Name']


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def validate_schema(df):
    if not all(col in df.columns for col in EXPECTED_COLUMNS):
        return {"error": f"The Excel file must contain the following columns: {', '.join(EXPECTED_COLUMNS)}"}


def analyze_excel(df):
    null_values = df.isnull().sum().to_dict()
    return null_values


@app.post("/analyze_excel/")
async def analyze_excel_endpoint(file: UploadFile = File(...)):
    try:
        if not allowed_file(file.filename):
            return {"error": "Invalid file type. Please upload an Excel file."}

        if file.content_length > MAX_FILE_SIZE_BYTES:
            return {"error": "File size exceeds the maximum limit of 10MB. Please upload a smaller file."}

        with open("uploaded_file.xlsx", "wb") as f:
            f.write(file.file.read())

        df = pd.read_excel("uploaded_file.xlsx")

        validation_result = validate_schema(df)
        if validation_result.get("error"):
            return validation_result

        analysis_results = analyze_excel(df)

        return analysis_results

    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}
