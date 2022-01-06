import logging
import logging.config
from datetime import datetime

import pandas as pd


FULL_DATASET = False
TARGET_PROTEIN = "Spike"
SAMPLE_END_DATE = datetime(2020, 4, 1)
MUTATION_SCORE = 1
# MISSING_SCORE = 0.01

MUTATION_PER_SEQ_FILE = "Output/mutation_per_seq.csv"

TRAINING_DATA_FILE = "Output/training_data.csv"

logging.config.fileConfig("logging.conf")

logging.info("Load data...")
mutation_per_seq: pd.DataFrame = pd.read_csv(
    MUTATION_PER_SEQ_FILE,
    nrows=None if FULL_DATASET else 1000000
)
mutation_per_seq["Value"] = MUTATION_SCORE

mutation_per_seq["Date"] = pd.to_datetime(mutation_per_seq["Date"])
mutation_per_seq = mutation_per_seq[mutation_per_seq["Date"] < SAMPLE_END_DATE]
logging.info(f"{mutation_per_seq['Accession'].nunique()} seqs before {SAMPLE_END_DATE.strftime('%Y-%m-%d')}")

mutation_per_seq = mutation_per_seq[mutation_per_seq["Mutation"].str.contains(TARGET_PROTEIN)]
logging.info(f"{mutation_per_seq['Accession'].nunique()} seqs are on {TARGET_PROTEIN}")

training_data = mutation_per_seq
# training_data = mutation_per_seq.pivot_table(
#     index="Accession",
#     columns="Mutation",
#     values="Value",
#     fill_value=MISSING_SCORE
# )
# training_data = pd.DataFrame(training_data.stack(), columns=["Value"]).reset_index()

seq_names = pd.DataFrame(mutation_per_seq["Accession"].unique(), columns=["Accession"])
seq_names["Seq_id"] = seq_names.index
mut_names = pd.DataFrame(mutation_per_seq["Mutation"].unique(), columns=["Mutation"])
mut_names["Mut_id"] = mut_names.index

training_data = training_data.merge(seq_names, on="Accession")
training_data = training_data.merge(mut_names, on="Mutation")

training_data.to_csv(TRAINING_DATA_FILE, index=False)
