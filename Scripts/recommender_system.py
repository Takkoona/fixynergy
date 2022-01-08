import logging
import logging.config

import pandas as pd
import torch
from torch.utils.data.dataset import Dataset
from torch.utils.data import DataLoader
from matplotlib import pyplot as plt


TRAINING_DATA_FILE = "Output/training_data.csv"

FIXYNERGY_MODEL = "Output/fixynergy.pth"
TRAINING_LOSSES_PLOT = "Plots/training_losses.pdf"

logging.config.fileConfig("logging.conf")


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

    def forward(self, x):
        seqs, muts = x[:, 0], x[:, 1]
        seq_vec = self.seq_embedding(seqs)
        mut_vec = self.mut_embedding(muts)
        x = torch.cat([seq_vec, mut_vec], dim=1)
        x = self.hidden(x)
        return torch.sigmoid(x)
        # return torch.mul(seq_vec, mut_vec).sum(dim=1)


class MutationDataset(Dataset):

    def __init__(self, seq_mut: pd.DataFrame) -> None:
        super().__init__()
        self.seq_mut = seq_mut

        self.seq_ids = seq_mut["Seq_id"].unique()
        self.mut_ids = seq_mut["Mut_id"].unique()
        logging.info(f"{len(self.seq_ids)} seqs and {len(self.mut_ids)} muts")

        self.seq_id2name = self.id2name("Seq_id", "Accession")
        self.mut_id2name = self.id2name("Mut_id", "Mutation")

        self.X = self.seq_mut[["Seq_id", "Mut_id"]].values
        self.y = self.seq_mut["Value"].values

    def __len__(self):
        return len(self.seq_mut)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

    def id2name(self, id_col, name_col):
        res = self.seq_mut[[name_col, id_col]]
        res = res.drop_duplicates()
        res = res.set_index(id_col, drop=True)
        return res[name_col].sort_index()


def main(device):

    seq_mut = pd.read_csv(TRAINING_DATA_FILE)
    n_factors = 10

    batch_size = 128
    shuffle = True
    learning_rate = 1e-3
    weight_decay = 1e-5
    n_epochs = 100

    training_data = MutationDataset(seq_mut)
    training_iter = DataLoader(
        training_data,
        batch_size=batch_size,
        shuffle=shuffle
    )

    model_args = {
        "n_seqs": len(training_data.seq_ids),
        "n_muts": len(training_data.mut_ids),
        "n_factors": n_factors
    }

    model = Fixynergy(**model_args)
    model.to(device)
    loss_fn = torch.nn.MSELoss(reduction="sum")
    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=learning_rate,
        weight_decay=weight_decay
    )

    losses = []
    model.train()
    for epoch in range(n_epochs):
        for X, y in training_iter:
            X: torch.Tensor = X.to(device)
            y: torch.Tensor = y.to(device)
            pred: torch.Tensor = model(X)

            y = y.float().view(pred.size())
            loss: torch.Tensor = loss_fn(pred, y)

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        logging.info(f"{epoch + 1}/{n_epochs}, loss: {loss.item()}")
        losses.append({
            "epoch": epoch,
            "loss": loss.item()
        })

    losses = pd.DataFrame.from_records(losses, index="epoch")
    losses = losses[losses.index > n_epochs * 0.2]
    plt.plot(losses["loss"])
    plt.savefig(TRAINING_LOSSES_PLOT)
    logging.info(f"{TRAINING_LOSSES_PLOT} saved!")

    torch.save({
        "model_args": model_args,
        "model_state_dict": model.state_dict()
    }, FIXYNERGY_MODEL)
    logging.info(f"{FIXYNERGY_MODEL} saved!")


if __name__ == "__main__":
    use_cuda = torch.cuda.is_available()
    # use_cuda = False
    device = torch.device("cuda:0" if use_cuda else "cpu")
    main(device)
