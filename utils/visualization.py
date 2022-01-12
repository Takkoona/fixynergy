from matplotlib import pyplot as plt

import pandas as pd
from sklearn.preprocessing import StandardScaler
from umap import UMAP


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
