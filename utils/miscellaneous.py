import pickle

import numpy as np
import pandas as pd


def get_mut_percentage(c_date, AVERAGE_PERIOD, area, bg_num: dict, mutation_num: dict):
    date_span = pd.date_range(
        end=c_date,
        periods=AVERAGE_PERIOD
    ).strftime("%Y-%m-%d")

    daily_average = _mean_span_dates(bg_num, date_span)
    if daily_average > 20:
        mut_percentage = {
            mut: _mean_span_dates(mut_info[area], date_span) / daily_average
            for mut, mut_info in mutation_num.items()
            if area in mut_info
        }
        return {"Date": c_date, **mut_percentage}
    else:
        return None


def _mean_span_dates(daily_num: dict, date_span: list):
    return np.mean(daily_num.get(d, 0) for d in date_span)


def mut_seq_info(df: pd .DataFrame):
    mut_n = df['Mutation'].nunique()
    seq_n = df['Accession'].nunique()
    return f"{mut_n} mutations of {seq_n} seqs"


def aa_per_seq(ac: str, ac_group: pd.DataFrame, pos_info: pd.DataFrame, all_mut_comb):
    ac_group = ac_group.sort_values("Pos")
    (c_date,) = ac_group["Date"].unique()
    (lineage, ) = ac_group["Lineage"].unique()
    mut_set = ",".join(ac_group["Pos"].astype(str) + ac_group["To"])

    aa_info = pd.concat([
        ac_group[["To", "Pos", "Pos_id"]],
        pos_info[~pos_info["Pos"].isin(ac_group["Pos"].values)]
    ])
    aa_info["Mut_set"] = mut_set
    all_mut_comb[mut_set] = aa_info

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
        _best_scored_AA(ac, row["Pos"], row[aa_table.values])
        for _, row in ac_group.iterrows()
    ])


def _best_scored_AA(ac: str, pos: int, row_aa: pd.Series):
    best_scored_index = np.argmax(row_aa)
    return {
        "Accession": ac,
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


def combo_daily_count(
    all_mut_combo: set,
    future_possible_combo_id: dict,
    future_combo_dated: dict,
    combo_file: str,
    id_file: str
):
    res = []
    id2combo = {}
    for combo in all_mut_combo:
        combo_id = future_possible_combo_id[combo]
        id2combo[combo_id] = tuple(combo)
        for c_date, c_date_combo in future_combo_dated.items():
            combo_freq = c_date_combo[combo]
            if combo_freq:
                res.append({
                    "Combo_id": combo_id,
                    "Date": c_date,
                    "Combo_count": combo_freq,
                })

    res = pd.DataFrame.from_dict(res)
    res.to_feather(combo_file)
    with open(id_file, "wb") as f:
        pickle.dump(id2combo, f)


def area_combo_count(
    combo_per_ac: list,
    captured_combo: list,
    missed_combo: list,
    c_date,
    area,
):
    ac_captured = 0
    ac_missed = 0
    for ac_combos in combo_per_ac:
        n_captured = 0
        n_missed = 0
        for combo in ac_combos:
            n_captured += combo in captured_combo
            n_missed += combo in missed_combo
        ac_captured += bool(n_captured)
        ac_missed += bool(n_missed)
    return {
        "Area": area,
        "Date": c_date,
        "AC_captured": ac_captured,
        "AC_missed": ac_missed,
        "AC_total": len(combo_per_ac)
    }
