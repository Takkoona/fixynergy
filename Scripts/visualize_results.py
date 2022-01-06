import pandas as pd
from matplotlib import pyplot as plt

MUTATION_EMBEDDINGS_FILE = "Output/mutation_embeddings.csv"

mut_embbedings = pd.read_csv(MUTATION_EMBEDDINGS_FILE, index_col=0)

print(mut_embbedings.mean(axis=1).sort_values())
