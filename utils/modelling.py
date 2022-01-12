import logging

import numpy as np
import pandas as pd
import torch
from torch.utils.data.dataset import Dataset


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
        self.data = self.seq_mut[[
            "Seq_id", "Mut_id", "Value"]].values[self.mask]
        # logging.info(f"{len(drop_index)} dropped, {len(self)} remaining")
        self.mask[drop_index] = True
