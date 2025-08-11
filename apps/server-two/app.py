import os
import pandas as pd
import uvicorn
from fastapi import FastAPI
from verse import common

DATA_PATH = os.environ.get("DATA_PATH", "/static_data/LD2011_2014.csv")

app = FastAPI()
logging = common.logging


@app.get("/corr/{meter_id}")
def corr(meter_id: str):
    k, v = find_most_correlated_meter(meter_id)
    return {"meter": k, "corr": v}


@app.get("/metrics/memory")
def metrics():
    return common.get_memory_usage()


def find_most_correlated_meter(m: str) -> tuple[str, float]:
    ix = int(m.split("_")[1]) - 1
    corrs = app.corr_matrix[ix]
    mt, max_corr = "MT_000", float("-inf")
    for i, c in enumerate(corrs):
        if i == ix:
            continue
        if c > max_corr:
            mt, max_corr = f"MT_{str(i).zfill(3)}", c
    return mt, max_corr


def _load_meter_data() -> pd.DataFrame:
    logging.info("mem_before_data_load", mem=common.get_memory_usage())
    logging.info("loading_meter_data", source=DATA_PATH)
    df = common.load_data(DATA_PATH, delimiter=";", decimal=",")
    logging.info("mem_after_data_load", mem=common.get_memory_usage())
    return df


if __name__ == "__main__":
    df = _load_meter_data()
    app.corr_matrix = common.corr(df, common.get_meter_cols(df))
    uvicorn.run(app, host="0.0.0.0", port=8080)
