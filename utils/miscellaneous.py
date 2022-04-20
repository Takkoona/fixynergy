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
    aa_table: pd.Series,
):
    return pd.DataFrame.from_records([
        _best_scored_AA(ac, row["Pos"], row["Protein"], row[aa_table.values])
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


def select_mut_AA(
    dummy: str,
    dummy_group: pd.DataFrame,
    aa_table: pd.Series,
    muts: list,
):
    aa_df = extract_AA(dummy, dummy_group, aa_table)
    aa_info = aa_df["Pos"].astype(str) + aa_df["AA"]
    aa_info = aa_info[aa_info.isin(muts)]
    return aa_df


def remove_same_site_combo(all_mut_combo) -> set:
    all_possible_mut_combo = []
    for combo in all_mut_combo:
        prev_site = -1
        to_keep = True
        for mut in combo:
            site = int("".join(filter(str.isdigit, mut)))
            if site == prev_site:
                to_keep = False
                break
            prev_site = site
        if to_keep:
            all_possible_mut_combo.append(combo)

    return set(all_possible_mut_combo)


def area_combo_count(
    combo_per_ac: list,
    sampled_captured: list,
    sampled_missed: list,
    c_date,
    area,
    nth_comparison
):
    # logging.info(f"{nth_comparison} {c_date} {area}")
    ac_captured = 0
    ac_missed = 0
    for ac_combos in combo_per_ac:
        n_captured = 0
        n_missed = 0
        for combo in ac_combos:
            n_captured += frozenset(combo) in sampled_captured
            n_missed += frozenset(combo) in sampled_missed
        ac_captured += bool(n_captured)
        ac_missed += bool(n_missed)
    return {
        "Area": area,
        "Date": c_date,
        "AC_captured": ac_captured,
        "AC_missed": ac_missed,
        "AC_total": len(combo_per_ac),
        "nth_comparison": nth_comparison
    }
