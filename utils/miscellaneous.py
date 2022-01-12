import logging
from statistics import mean

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
