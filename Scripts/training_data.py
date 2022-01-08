import logging
import logging.config
from datetime import datetime

import pandas as pd


TARGET_PROTEIN = "Spike"
SAMPLE_END_DATE = datetime(2020, 8, 1)
MUTATION_SCORE = 1
MISSING_PENALTY = 0

MUTATION_PER_SEQ_FILE = "Output/mutation_per_seq.feather"

TRAINING_DATA_FILE = "Output/training_data.csv"


def mut_seq_info(df: pd .DataFrame):
    mut_n = df['Mutation'].nunique()
    seq_n = df['Accession'].nunique()
    return f"{mut_n} mutations of {seq_n} seqs"


logging.config.fileConfig("logging.conf")

logging.info("Load data...")
df: pd.DataFrame = pd.read_feather(MUTATION_PER_SEQ_FILE)
df["Value"] = MUTATION_SCORE

df["Date"] = pd.to_datetime(df["Date"])
df = df[df["Date"] < SAMPLE_END_DATE]
logging.info(f"{mut_seq_info(df)} before {SAMPLE_END_DATE}")

df = df[df["Mutation"].str.contains(TARGET_PROTEIN)]
logging.info(f"{mut_seq_info(df)} are on {TARGET_PROTEIN}")

df = df[~df["Mutation"].str.contains("stop")]
logging.info(f"{mut_seq_info(df)} has no stop codon")

seq_info = df[["Accession", "Lineage", "Date"]].drop_duplicates()
seq_info = seq_info.set_index("Accession")

# training_data = df
training_data = df.pivot_table(
    index="Accession",
    columns="Mutation",
    values="Value",
    fill_value=MISSING_PENALTY
)
training_data = pd.DataFrame(
    training_data.drop_duplicates().stack(),
    columns=["Value"]
)
training_data = training_data[training_data["Value"] != MISSING_PENALTY]

training_data["Lineage"] = seq_info.loc[
    training_data.index.get_level_values("Accession"),
    "Lineage"
].values
training_data["Date"] = seq_info.loc[
    training_data.index.get_level_values("Accession"),
    "Date"
].values
training_data = training_data.reset_index()
logging.info(f"{mut_seq_info(training_data)} are unique")

seq_names = pd.DataFrame(
    training_data["Accession"].unique(),
    columns=["Accession"]
)
seq_names["Seq_id"] = seq_names.index
mut_names = pd.DataFrame(
    training_data["Mutation"].unique(),
    columns=["Mutation"]
)
mut_names["Mut_id"] = mut_names.index

training_data = training_data.merge(seq_names, on="Accession")
training_data = training_data.merge(mut_names, on="Mutation")

training_data = training_data.sort_values("Accession")
training_data = training_data.sort_values("Date")
training_data.to_csv(TRAINING_DATA_FILE, index=False)
logging.info(f"{TRAINING_DATA_FILE} saved!")
