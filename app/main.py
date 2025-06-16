from fastapi import FastAPI, UploadFile, File, HTTPException
from app import models, database
from app.database import SessionLocal
import csv
from io import StringIO
from datetime import datetime

app = FastAPI()
models.Base.metadata.create_all(bind=database.engine)

# Mapear nombre del archivo con modelo y columnas esperadas
FILE_CONFIG = {
    "employees.csv": {
        "model": models.Employee,
        "columns": ["id", "name", "datetime", "department_id", "job_id"],
        "types": [int, str, lambda x: datetime.fromisoformat(x.replace("Z", "")), int, int]
    },
    "departments.csv": {
        "model": models.Department,
        "columns": ["id", "department"],
        "types": [int, str]
    },
    "jobs.csv": {
        "model": models.Job,
        "columns": ["id", "job"],
        "types": [int, str]
    }
}

@app.post("/upload_csv")
async def upload_csv(file: UploadFile = File(...)):
    config = FILE_CONFIG.get(file.filename)
    if not config:
        raise HTTPException(status_code=400, detail="Archivo no soportado")

    try:
        content = await file.read()
        decoded = content.decode("utf-8")
        reader = csv.reader(StringIO(decoded))
        db = SessionLocal()
        inserted = 0

        for row in reader:
            parsed_row = {}
            for idx, (col, cast_fn) in enumerate(zip(config["columns"], config["types"])):
                value = row[idx].strip()
                parsed_row[col] = cast_fn(value) if value else None

            # Validación mínima
            if not parsed_row.get("id"):
                continue

            db.add(config["model"](**parsed_row))
            inserted += 1

        db.commit()
        return {"status": "success", "rows_inserted": inserted}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
