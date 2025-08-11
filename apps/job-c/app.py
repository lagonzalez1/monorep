import numpy as np
import os
import pandas as pd
from verse import common


DATA_PATH = os.environ.get("DATA_PATH", "/static_data/enron_emails_1702.csv")

logging = common.logging


@common.elapsed_time
def load() -> pd.DataFrame:
    logging.info("loading_data", msg="loading email data", source=DATA_PATH)
    return pd.read_csv(DATA_PATH)


@common.elapsed_time
def main():
    logging.info("job_starting")
    df = load()
    N = 10
    logging.info("splice", msg=f"vector splicing first {N} emails")
    arr = df.content[:N].values.astype(str)
    s = np.strings.slice(arr, 80)
    logging.debug("result", slices=s)
    logging.info("job_complete")


@common.profile_memory
def cleanup():
    pass


if __name__ == "__main__":
    main()
    cleanup()
