import numpy as np
import pandas as pd
import psutil
import structlog
import time

from pathlib import Path

logging = structlog.get_logger("BaseStructLogger")


def get_memory_usage() -> float:
    """Returns the RSS memory usage of the current process in MB."""
    process = psutil.Process()
    mem_info = process.memory_info()
    return mem_info.rss / (1024**2)


def profile_memory(func):
    """This is a function decorator around `get_memory_usage()` to log RSS memory"""

    def inner(*args, **kwargs):
        logging.info("memory_usage_snapshot", mb=float(f"{get_memory_usage():.2f}"))
        return func(*args, **kwargs)

    return inner


def elapsed_time(func):
    """Decorator that logs the elapsed time in human readable format"""

    def inner(*args, **kwargs):
        start = time.time()
        res = func(*args, **kwargs)
        end = time.time()
        elapsed = end - start
        _mins = int(elapsed // 60)
        _secs = elapsed % 60
        logging.info("elapsed_time", duration=f"{_mins} mins {_secs:.3f} secs")
        return res

    return inner


def load_data(path: Path, **kwargs) -> pd.DataFrame:
    """Loads CSV file as a Pandas Data Frame"""
    return pd.read_csv(path, **kwargs)


def get_meter_cols(df: pd.DataFrame) -> list[str]:
    """Returns a list of relevant meter series column names for this exercise"""
    return [col for col in df.columns if col.startswith("MT_")]


def corr(df: pd.DataFrame, selected_cols: list[str]) -> np.ndarray:
    """Returns the correlation matrix of `df` as an ndarray"""
    return np.corrcoef(df[selected_cols].values.T)
