from fastapi import FastAPI
from fastapi.responses import FileResponse
import os

app = FastAPI()

# Path to the Excel file
excel_file = "./trade_results/trade_results.xlsx"

@app.get("/download-history", summary="Download Excel", response_description="Download trade results Excel file")
async def download_excel():
    # Check if the file exists
    if os.path.exists(excel_file):
        return FileResponse(
            path=excel_file,
            filename="trade_results.xlsx",
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    else:
        return {"error": "File not found"}


