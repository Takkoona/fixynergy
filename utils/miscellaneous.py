import logging
from statistics import mean

import numpy as np
import pandas as pd


def get_mut_percentage(c_date, AVERAGE_PERIOD, area, bg_num: dict, mutation_num: dict):
    logging.info(f"{area} {c_date}")

    date_span = pd.date_range(
        end=c_date,
        periods=AVERAGE_PERIOD
    ).strftime("%Y-%m-%d")

    daily_average = mean(bg_num.get(d, 0) for d in date_span)
    if daily_average > 20:
        return {"Date": c_date, **{mut: mean(mut_info[area].get(d, 0)
                                             for d in date_span) / daily_average
                                   for mut, mut_info in mutation_num.items()
                                   if area in mut_info}}
    else:
        return None


def mut_seq_info(df: pd .DataFrame):
    mut_n = df['Mutation'].nunique()
    seq_n = df['Accession'].nunique()
    return f"{mut_n} mutations of {seq_n} seqs"


def aa_per_seq(ac: str, ac_group: pd.DataFrame, pos_info: pd.DataFrame, aa_info_dict):
    (c_date,) = ac_group["Date"].unique()
    (lineage, ) = ac_group["Lineage"].unique()
    mut_set = frozenset(ac_group["To"] + ac_group["Pos"].astype(str))

    aa_info = pd.concat([
        ac_group[["To", "Pos", "Pos_id"]],
        pos_info[~pos_info["Pos"].isin(ac_group["Pos"].values)]
    ])
    aa_info["Accession"] = ac
    aa_info["Date"] = c_date
    aa_info["Lineage"] = lineage

    aa_info_dict[mut_set] = aa_info


def calculate_pred_AA(ac: str, ac_group: pd.DataFrame, aa_table: pd.Series):
    res = [
        {
            "Accession": ac,
            "Pos": row["Pos"],
            "AA": aa_table[np.argmax(row[aa_table.values])]
        }
        for _, row in ac_group.iterrows()
    ]
    return pd.DataFrame.from_records(res)
