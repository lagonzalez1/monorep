import csv
import os
import pandas as pd
from verse import common
from sentence_transformers import SentenceTransformer


DATA_PATH = os.environ.get("DATA_PATH", "/static_data/enron_emails_1702.csv")

logging = common.logging


@common.elapsed_time
def load():
    logging.info("loading_data", msg="loading embedding model and email data", source=DATA_PATH)
    model = SentenceTransformer("all-MiniLM-L6-v2")
    df = pd.read_csv(DATA_PATH)
    return model, df


@common.elapsed_time
def main(): 
    logging.info("job_starting")
    logging.info("loading_data", source=DATA_PATH)
    model, df = load()

    N = 10
    outfile="output.csv"
    logging.info("create_embeddings", msg=f"generate embedding vectors for first {N} emails", output_path=outfile)
    with open(outfile, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        for s in df.content[:N]:
            logging.debug("create_embeddings", msg="encoding and saving to CSV", email=s[:1024])
            v = model.encode(s)
            writer.writerow(v)

    logging.info("job_complete")


@common.profile_memory
def cleanup():
    pass

if __name__ == "__main__":
    main()
    cleanup()
