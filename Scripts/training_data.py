import logging
import logging.config
from datetime import datetime

import pandas as pd


FULL_DATASET = False
TARGET_PROTEIN = "Spike"
SAMPLE_END_DATE = datetime(2020, 4, 1)
MUTATION_SCORE = 1
MISSING_SCORE = 0

MUTATION_PER_SEQ_FILE = "Output/mutation_per_seq.csv"

TRAINING_DATA_FILE = "Output/training_data.csv"

logging.config.fileConfig("logging.conf")

logging.info("Load data...")
df: pd.DataFrame = pd.read_csv(
    MUTATION_PER_SEQ_FILE,
    nrows=None if FULL_DATASET else 1000000
)
df["Value"] = MUTATION_SCORE

df["Date"] = pd.to_datetime(df["Date"])
df = df[df["Date"] < SAMPLE_END_DATE]
logging.info(
    f"{df['Mutation'].nunique()} of {df['Accession'].nunique()} seqs before {SAMPLE_END_DATE.strftime('%Y-%m-%d')}")

df = df[df["Mutation"].str.contains(TARGET_PROTEIN)]
logging.info(
    f"{df['Mutation'].nunique()} of {df['Accession'].nunique()} seqs are on {TARGET_PROTEIN}")

seq_info = df[["Accession", "Lineage", "Date"]].drop_duplicates()
seq_info = seq_info.set_index("Accession")

# training_data = df
training_data = df.pivot_table(
    index="Accession",
    columns="Mutation",
    values="Value",
    fill_value=MISSING_SCORE
)
training_data = pd.DataFrame(
    training_data.drop_duplicates().stack(),
    columns=["Value"]
)
training_data = training_data[training_data["Value"] != 0]
training_data["Lineage"] = seq_info.loc[training_data.index.get_level_values("Accession"), "Lineage"].values
training_data["Date"] = seq_info.loc[training_data.index.get_level_values("Accession"), "Date"].values
training_data = training_data.reset_index()

seq_names = pd.DataFrame(df["Accession"].unique(), columns=["Accession"])
seq_names["Seq_id"] = seq_names.index
mut_names = pd.DataFrame(df["Mutation"].unique(), columns=["Mutation"])
mut_names["Mut_id"] = mut_names.index

training_data = training_data.merge(seq_names, on="Accession")
training_data = training_data.merge(mut_names, on="Mutation")

training_data.to_csv(TRAINING_DATA_FILE, index=False)
