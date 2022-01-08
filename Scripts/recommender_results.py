import logging
import logging.config

import numpy as np
import pandas as pd
import torch

from recommender_system import Fixynergy

TRAINING_DATA_FILE = "Output/training_data.csv"
FIXYNERGY_MODEL = "Output/fixynergy.pth"

EMBEDDINGS_SEQ_FILE = "Output/embeddings_seq.csv"
EMBEDDINGS_MUT_FILE = "Output/embeddings_mut.csv"
MUTATION_SCORES_FILE = "Output/mutation_scores.csv"
MUTATION_SCORES_2_FILE = "Output/mutation_scores_2.csv"

logging.config.fileConfig("logging.conf")


def id2name(seq_mut: pd.DataFrame, id_col, name_col):
    res = seq_mut[[name_col, id_col]]
    res = res.drop_duplicates()
    res = res.set_index(id_col, drop=True)
    return res[name_col].sort_index()


logging.info("Loading data..")
seq_mut: pd.DataFrame = pd.read_csv(TRAINING_DATA_FILE)

seq_id2name = id2name(seq_mut, "Seq_id", "Accession")
mut_id2name = id2name(seq_mut, "Mut_id", "Mutation")

use_cuda = torch.cuda.is_available()
device = torch.device("cuda:0" if use_cuda else "cpu")

model_params = torch.load(FIXYNERGY_MODEL)
model = Fixynergy(**model_params["model_args"])
model.load_state_dict(model_params["model_state_dict"])
model.to(device)

logging.info("Mutation score matrix")
model.eval()
with torch.no_grad():
    n_muts = len(mut_id2name)
    n_seqs = len(seq_id2name)
    mutation_scores = np.zeros((n_seqs, n_muts))
    for seq_id in seq_id2name.index:
        X = np.column_stack((
            np.full(n_muts, seq_id),
            mut_id2name.index
        ))
        X = torch.Tensor(X).int().to(device)
        pred: torch.Tensor = model(X)
        (pred, ) = pred.data.cpu().numpy().T
        mutation_scores[seq_id, :] = pred

mutation_scores = pd.DataFrame(
    mutation_scores,
    index=seq_id2name.values,
    columns=mut_id2name.values
)

mutation_scores.to_csv(MUTATION_SCORES_FILE)
logging.info(f"{MUTATION_SCORES_FILE} saved!")


mut_embbedings = model.mut_embedding.weight.data.cpu().numpy()
mut_embbedings = pd.DataFrame(
    mut_embbedings,
    columns=[f"comb_{n}" for n in range(model.n_factors)],
    index=mut_id2name
)
mut_embbedings.to_csv(EMBEDDINGS_MUT_FILE)
logging.info(f"{EMBEDDINGS_MUT_FILE} saved!")

seq_embbedings = model.seq_embedding.weight.data.cpu().numpy()
seq_embbedings = pd.DataFrame(
    seq_embbedings,
    columns=[f"comb_{n}" for n in range(model.n_factors)],
    index=seq_id2name
)
seq_embbedings.to_csv(EMBEDDINGS_SEQ_FILE)
logging.info(f"{EMBEDDINGS_SEQ_FILE} saved!")

mutation_scores_2 = seq_embbedings.dot(mut_embbedings.T)
mutation_scores_2.to_csv(MUTATION_SCORES_2_FILE)
logging.info(f"{MUTATION_SCORES_2_FILE} saved!")
