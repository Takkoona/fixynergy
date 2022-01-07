import pandas as pd
from matplotlib import pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

FULL_DATASET = False

TRAINING_DATA_FILE = "Output/training_data.csv"
SEQUENCE_EMBEDDINGS_FILE = "Output/sequence_embeddings.csv"
MUTATION_EMBEDDINGS_FILE = "Output/mutation_embeddings.csv"

SEQUENCE_MUTATION_PLOT = "Plots/sequence_mutation_pca.pdf"
SEQUENCE_EMBEDDINGS_PLOT = "Plots/sequence_embeddings_pca.pdf"


def plot_pca(
    df: pd.DataFrame,
    seq_lineage: pd.DataFrame,
    plot_name: str,
    min_label_counts: int = 500
):

    labels = seq_lineage.loc[df.index]["Lineage"]
    labels = labels.str[0:5]
    label_counts = labels.value_counts()
    selected_labels = label_counts[(label_counts > min_label_counts) & (
        label_counts.index != "None")].index[1:]
    print(label_counts)
    print(selected_labels)

    X = StandardScaler().fit_transform(df)
    pca = PCA(n_components=2)
    embeddings = pca.fit_transform(X)

    embeddings = pd.DataFrame(embeddings, columns=["PC1", "PC2"])
    embeddings["Label"] = labels.values
    embeddings = embeddings[embeddings["Label"].isin(selected_labels)]

    fig, ax = plt.subplots(
        nrows=1,
        ncols=1,
        figsize=(6, 6)
    )

    for label, group in embeddings.groupby("Label"):
        ax.scatter(
            group["PC1"],
            group["PC2"],
            label=label,
            alpha=0.3
        )
    ax.legend()

    plt.savefig(plot_name)
    plt.close()


training_data: pd.DataFrame = pd.read_csv(TRAINING_DATA_FILE)

seq_lineage = training_data[["Accession", "Lineage"]].drop_duplicates()
seq_lineage = seq_lineage.set_index("Accession")

seq_mutations = training_data.pivot_table(
    index="Accession",
    columns="Mutation",
    values="Value",
    fill_value=0
)
seq_mutations = seq_mutations.drop_duplicates()

seq_embbeddings = pd.read_csv(SEQUENCE_EMBEDDINGS_FILE, index_col=0)

plot_pca(seq_mutations, seq_lineage, SEQUENCE_MUTATION_PLOT, min_label_counts=10)
plot_pca(seq_embbeddings, seq_lineage, SEQUENCE_EMBEDDINGS_PLOT)

# mut_embbedings = pd.read_csv(MUTATION_EMBEDDINGS_FILE, index_col=0)

# # print(mut_embbedings.mean(axis=1).sort_values())

# for col in mut_embbedings:
#     col = mut_embbedings[col].sort_values()
#     n_positive = len(col[col > 0].index)
#     n_negative = len(col[col < 0].index)
#     print("Positive / Negative", n_positive / n_negative)
