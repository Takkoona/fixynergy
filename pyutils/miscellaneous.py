import numpy as np
import pandas as pd


def aa_per_seq(ac: str, ac_group: pd.DataFrame, pos_info: pd.DataFrame, all_aa_comb):
    # Sort by 'Pos' so won't be unmatched duplicates
    ac_group = ac_group.sort_values("Pos")
    # Get date and lineage info
    (c_date,) = ac_group["Date"].unique()
    (lineage,) = ac_group["Lineage"].unique()
    # Mutation for each ac separated by comma
    mut_set = ",".join(ac_group["Protein"] + "_" +
                       ac_group["Pos"].astype(str) + ac_group["To"])

    # 'aa_info' is the amino acid state for all sites (mutated and unmutated)
    aa_info = pd.concat([
        ac_group[["Protein", "To", "Pos"]],
        pos_info[~pos_info["Pos"].isin(
            ac_group["Pos"].values)]  # unmutated 'Pos'
    ])
    aa_info["Mut_set"] = mut_set
    # Append 'aa_info' to 'all_mut_comb' which is a 'dict'.
    # The same 'mut_set' will have the same 'aa_info'
    all_aa_comb[mut_set] = aa_info

    return {
        "Mut_set": mut_set,
        "Accession": ac,
        "Date": c_date,
        "Lineage": lineage
    }


def extract_AA(
    ac: str,
    ac_group: pd.DataFrame,
    aa_names: list,
):
    return pd.DataFrame.from_records([
        _best_scored_AA(ac, row["Pos"], row["Protein"], row[aa_names])
        for _, row in ac_group.iterrows()
    ])


def _best_scored_AA(ac: str, pos: int, protein: str, row_aa: pd.Series):
    best_scored_index = np.argmax(row_aa)
    return {
        "Accession": ac,
        "Protein": protein,
        "Pos": pos,
        "AA": row_aa.index[best_scored_index],
        "Score": row_aa.values[best_scored_index]
    }


def sort_mut_by_pos(
    df: pd.DataFrame,
    ref_mut_col: str,
    mut_col: str,
):
    df, ref_protein_col, ref_pos_col = _separate_protein_pos(df, ref_mut_col)
    df, protein_col, pos_col = _separate_protein_pos(df, mut_col)
    return ref_pos_greater(
        df=df,
        ref_mut_col=ref_mut_col,
        ref_protein_col=ref_protein_col,
        ref_pos_col=ref_pos_col,
        mut_col=mut_col,
        protein_col=protein_col,
        pos_col=pos_col,
    )


def ref_pos_greater(
    df: pd.DataFrame,
    ref_mut_col: str,
    ref_protein_col: str,
    ref_pos_col: str,
    mut_col: str,
    protein_col: str,
    pos_col: str
):
    df["Ref_pos_greater"] = ((df[ref_protein_col] == df[protein_col]) &
                             (df[ref_pos_col] > df[pos_col]))

    df[ref_mut_col], df[mut_col] = np.where(
        df["Ref_pos_greater"],
        [df[mut_col], df[ref_mut_col]],
        [df[ref_mut_col], df[mut_col]],
    )
    del df[ref_protein_col], df[ref_pos_col], df[protein_col], df[pos_col], df["Ref_pos_greater"]
    return df


def _separate_protein_pos(
    df: pd.DataFrame,
    mut_col: str,
):
    protein_col = mut_col + "_protein"
    pos_col = mut_col + "_pos"

    name_split = df[mut_col].str.split("_").str
    df[protein_col] = name_split[0]
    df[pos_col] = name_split[1].str.extract(r"(\d+)").astype(int)
    return df, protein_col, pos_col
