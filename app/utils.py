import pandas as pd
import io

async def parse_csv_to_dicts(file):
    contents = await file.read()
    df = pd.read_csv(io.StringIO(contents.decode()), names=["id", "name", "datetime", "department_id", "job_id"])
    # Cast explícito con pandas
    df["id"] = df["id"].astype(int)
    df["job_id"] = df["job_id"].astype("Int64")         # Soporta NaN
    df["department_id"] = df["department_id"].astype("Int64")
    if "datetime" in df.columns:
        df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")   
    return df.to_dict(orient="records")