import uvicorn
from fastapi import FastAPI
from verse.common import get_memory_usage

app = FastAPI()


@app.get("/echo/{msg}")
def echo(msg: str):
    return msg


@app.get("/metrics/memory")
def metrics():
    return get_memory_usage()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
