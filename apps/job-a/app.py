import csv
import os
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from verse import common

DATA_PATH = os.environ.get("DATA_PATH", "/static_data/LD2011_2014.csv")

logging = common.logging


@common.elapsed_time
def main():
    logging.info("job_starting")
    logging.info("loading_data", source=DATA_PATH)
    df = common.load_data(DATA_PATH, delimiter=";", decimal=",")
    data = df.drop(columns=['Unnamed: 0']).to_numpy()  # drop the time stamp column

    dim = 2
    logging.info("calculating_pca", n_components=dim)
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(data.T)
    pca = PCA(n_components=dim)
    principal_components = pca.fit_transform(scaled_data)
    
    outfile="output.csv"
    logging.info("writing_principal_components", output_path=outfile)
    with open(outfile, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(principal_components)

    logging.info("job_complete")


@common.profile_memory
def cleanup():
    pass


if __name__ == "__main__":
    main()
    cleanup()
