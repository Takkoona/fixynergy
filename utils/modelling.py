import numpy as np
import pandas as pd
import torch
from torch.utils.data.dataset import Dataset


class Fixynergy(torch.nn.Module):

    def __init__(self, n_seq, n_pos, n_factors, n_states) -> None:
        super().__init__()

        self.n_seq = n_seq
        self.n_pos = n_pos
        self.n_factors = n_factors

        self.seq_embedding = torch.nn.Embedding(n_seq, n_factors)
        self.mut_embedding = torch.nn.Embedding(n_pos, n_factors)

        self.seq_embedding.weight.data.uniform_(-0.01, 0.01)
        self.mut_embedding.weight.data.uniform_(-0.01, 0.01)

        n_conn = n_factors * 2
        self.hidden = torch.nn.Sequential(
            torch.nn.Linear(n_conn, n_conn),
            torch.nn.ReLU(),
            torch.nn.Linear(n_conn, n_conn),
            torch.nn.ReLU(),
            torch.nn.Linear(n_conn, n_states),
        )

    def forward(self, seq_ids, pos_ids):
        seq_vec = self.seq_embedding(seq_ids)
        mut_vec = self.mut_embedding(pos_ids)
        x = torch.cat([seq_vec, mut_vec], dim=1)
        return self.hidden(x)


class MutationDataset(Dataset):

    def __init__(self, seq_mut: pd.DataFrame) -> None:
        super().__init__()
        self.seq_mut = seq_mut

        self.seq_id2name = self.id2name("Seq_id", "Accession")
        self.pos_id2name = self.id2name("Pos_id", "Pos")

        self.n_seq = len(self.seq_id2name.values)
        self.n_pos = len(self.pos_id2name.values)

        self.n_states = seq_mut["AA_idx"].nunique()
        self.one_hot = np.eye(self.n_states)
        self.data_col = ["Seq_id", "Pos_id", "AA_idx"]
        self.data = self.seq_mut[self.data_col].values

        self.label_balance = {}
        pos_group: pd.DataFrame
        for _, pos_group in seq_mut.groupby("Pos"):
            aa_summary = pos_group["AA"].value_counts()
            for aa, num in (aa_summary - np.min(aa_summary)).items():
                self.label_balance[tuple(
                    pos_group.index[pos_group["AA"] == aa])] = num

        self.mask = np.ones(len(self.seq_mut), dtype=bool)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        seq, mut, value = self.data[idx, :]
        return (seq, mut), self.one_hot[:, value]

    def id2name(self, id_col, name_col):
        res = self.seq_mut[[name_col, id_col]]
        res = res.drop_duplicates()
        res = res.set_index(id_col, drop=True)
        return res[name_col].sort_index()

    def balance_values(self):
        for index, size in self.label_balance.items():
            drop_index = np.random.choice(
                index,
                size=size,
                replace=False,
            )
            self.mask[drop_index] = False
        self.data = self.seq_mut[self.data_col].values[self.mask]
        self.mask[drop_index] = True

    def fill_underrepresented(self):
        times_to_multiply = {}

        pos_group: pd.DataFrame
        for _, pos_group in self.seq_mut.groupby("Pos"):
            aa_summary = pos_group["AA"].value_counts()
            for aa, num in (np.max(aa_summary) / aa_summary).items():
                if num > 1:
                    times_to_multiply[tuple(
                        pos_group.index[pos_group["AA"] == aa])] = np.floor(num)

        self.data = self.seq_mut[self.data_col].values
        for index, num in times_to_multiply.items():
            for i in index:
                to_fill = np.tile(self.data[i], (np.int64(num), 1))
                self.data = np.vstack([self.data, to_fill])
