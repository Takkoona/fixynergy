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


def calculate_pred_AA(
    ac: str,
    ac_group: pd.DataFrame,
    aa_table: pd.Series,
    true_AA: pd.DataFrame
):
    return pd.DataFrame.from_records([
        {
            "Accession": ac,
            "Pos": row["Pos"],
            "AA": true_AA.loc[row["Pos"], "AA"] in (row[aa_table.values][row[aa_table.values] > 0]).index
        }
        for _, row in ac_group.iterrows()
    ])
