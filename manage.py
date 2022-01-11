import logging
import logging.config
from statistics import mean
from datetime import datetime

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import torch
from torch.utils.data.dataset import Dataset
from sklearn.preprocessing import StandardScaler
from umap import UMAP


AVERAGE_PERIOD = 14

TARGET_PROTEIN = "Spike"
SAMPLE_END_DATE = datetime(2020, 5, 1)
MUTATION_SCORE = 1
MISSING_PENALTY = 0

SITESMAPPING_FILE = "Data/sitesMapping.csv"
SURVEILLANCE_FILE = "Data/variant_surveillance.tsv"

MUTATION_PER_SEQ_FILE = "Output/mutation_per_seq.feather"
MUTATION_NUM_FILE = "Output/mutation_num.json"
BACKGROUND_NUM_FILE = "Output/background_num.json"

AREA_FIXED_DAILY_DIR = "Output/Area_fixed_daily"
FIXATION_LINKAGE_FILE = "Output/fixation_linkage.csv"

TRAINING_DATA_FILE = "Output/training_data.feather"

TRAINING_LOSSES_PLOT = "Plots/training_losses.pdf"
EMBEDDINGS_SEQ_FILE = "Output/embeddings_seq.csv"
EMBEDDINGS_MUT_FILE = "Output/embeddings_mut.csv"
MUTATION_SCORES_FILE = "Output/mutation_scores.csv"
MUTATION_SCORES_2_FILE = "Output/mutation_scores_2.csv"

SEQUENCE_MUTATION_PLOT = "Plots/sequence_mutation_pca.pdf"
SEQUENCE_EMBEDDINGS_PLOT = "Plots/sequence_embeddings_pca.pdf"

logging.config.fileConfig("logging.conf")


def get_mut_percentage(c_date, AVERAGE_PERIOD, area, bg_num: dict, mutation_num: dict):
    logging.info(f"{area} {c_date}")

    date_span = pd.date_range(
        end=c_date,
        periods=AVERAGE_PERIOD
    ).strftime("%Y-%m-%d")

    daily_average = mean(bg_num.get(d, 0) for d in date_span)
    if daily_average > 20:
        return {"Date": c_date, **{mut: mean(mut_info[area].get(d, 0)
                                             for d in date_span) / daily_average
                                   for mut, mut_info in mutation_num.items()
                                   if area in mut_info}}
    else:
        return None


def mut_seq_info(df: pd .DataFrame):
    mut_n = df['Mutation'].nunique()
    seq_n = df['Accession'].nunique()
    return f"{mut_n} mutations of {seq_n} seqs"


class Fixynergy(torch.nn.Module):

    def __init__(self, n_seqs, n_muts, n_factors) -> None:
        super().__init__()

        self.n_seqs = n_seqs
        self.n_muts = n_muts
        self.n_factors = n_factors

        self.seq_embedding = torch.nn.Embedding(n_seqs, n_factors)
        self.mut_embedding = torch.nn.Embedding(n_muts, n_factors)

        self.seq_embedding.weight.data.uniform_(0, 0.01)
        self.mut_embedding.weight.data.uniform_(0, 0.01)

        n_conn = n_factors * 2
        self.hidden = torch.nn.Sequential(
            torch.nn.Linear(n_conn, n_conn),
            torch.nn.ReLU(),
            torch.nn.Linear(n_conn, n_conn),
            torch.nn.ReLU(),
            torch.nn.Linear(n_conn, 1),
        )

    def forward(self, seq_ids, mut_ids):
        seq_vec = self.seq_embedding(seq_ids)
        mut_vec = self.mut_embedding(mut_ids)
        x = torch.cat([seq_vec, mut_vec], dim=1)
        x = self.hidden(x)
        return torch.sigmoid(x)
        # return torch.mul(seq_vec, mut_vec).sum(dim=1)


class MutationDataset(Dataset):

    def __init__(self, seq_mut: pd.DataFrame) -> None:
        super().__init__()
        self.seq_mut = seq_mut

        self.seq_id2name = self.id2name("Seq_id", "Accession")
        self.mut_id2name = self.id2name("Mut_id", "Mutation")

        self.n_seqs = len(self.seq_id2name.values)
        self.n_muts = len(self.mut_id2name.values)
        logging.info(f"{self.n_seqs} seqs and {self.n_muts} muts")

        positive_index = seq_mut.index[seq_mut["Value"] != 0]
        negative_index = seq_mut.index[seq_mut["Value"] == 0]
        n_positive = len(positive_index)
        n_negative = len(negative_index)
        logging.info(f"{n_positive} 1s and {n_negative} 0s")

        if n_positive > n_negative:
            self.oversampled_index = positive_index
            self.n_drop = n_positive - n_negative
        else:
            self.oversampled_index = negative_index
            self.n_drop = n_negative - n_positive
        self.mask = np.ones(len(self.seq_mut), dtype=bool)

        self.data = self.seq_mut[["Seq_id", "Mut_id", "Value"]].values

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        seq, mut, value = self.data[idx, :]
        return (seq, mut), value

    def id2name(self, id_col, name_col):
        res = self.seq_mut[[name_col, id_col]]
        res = res.drop_duplicates()
        res = res.set_index(id_col, drop=True)
        return res[name_col].sort_index()

    def balance_values(self):
        drop_index = np.random.choice(
            self.oversampled_index,
            self.n_drop,
            replace=False
        )
        self.mask[drop_index] = False
        self.data = self.seq_mut[["Seq_id", "Mut_id", "Value"]].values[self.mask]
        # logging.info(f"{len(drop_index)} dropped, {len(self)} remaining")
        self.mask[drop_index] = True


def plot_umap(
    df: pd.DataFrame,
    seq_lineage: pd.DataFrame,
    plot_name: str,
    min_label_counts: int = 50
):
    labels = seq_lineage.loc[df.index]["Lineage"]
    # labels = labels.str[0:5]
    label_counts = labels.value_counts()
    selected_labels = label_counts[
        (label_counts > min_label_counts) &
        (label_counts.index != "None")
    ].index

    X = StandardScaler().fit_transform(df)
    reducer = UMAP()
    embeddings = reducer.fit_transform(X)

    embeddings = pd.DataFrame(embeddings, columns=["umap1", "umap2"])
    embeddings["Label"] = labels.values
    embeddings = embeddings[embeddings["Label"].isin(selected_labels)]

    fig, ax = plt.subplots(
        nrows=1,
        ncols=1,
        figsize=(6, 6)
    )

    for label, group in embeddings.groupby("Label"):
        ax.scatter(
            group["umap1"],
            group["umap2"],
            label=label,
            alpha=0.5
        )
    ax.legend()

    plt.savefig(plot_name)


if __name__ == "__main__":
    import argparse
    logging.info("Using the command line")
