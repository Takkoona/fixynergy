import os
import logging
import logging.config
import json
from statistics import mean
from datetime import timedelta
from collections import defaultdict
from multiprocessing import Pool

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.dates import DateFormatter
from matplotlib import cm
from matplotlib.colors import rgb2hex
from sklearn.cluster import DBSCAN


MUTATION_NUM_FILE = "Output/mutation_num.json"
BACKGROUND_NUM_FILE = "Output/background_num.json"

AREA_FIXED_DAILY_DIR = "Output/Area_fixed_daily"
FIXATION_PERIOD_FILE = "Output/fixation_period.csv"

AVERAGE_PERIOD = 14

logging.config.fileConfig("logging.conf")

if not os.path.exists(AREA_FIXED_DAILY_DIR):
    os.mkdir(AREA_FIXED_DAILY_DIR)

def get_mut_percentage(c_date, AVERAGE_PERIOD, area, bg_num, mutation_num):
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
    
logging.info("Load data...")

with open(MUTATION_NUM_FILE) as f:
    mutation_num = json.load(f)
    
with open(BACKGROUND_NUM_FILE) as f:
    background_num = json.load(f)


area_labels = []
for area, bg_num in background_num.items():
    
    # if area not in ("Australia", "Austria"):
    #     continue
    
    bg_num_df = pd.DataFrame.from_records(
        {"d": d, "n": n}
        for d, n in bg_num.items()
    )
    
    if not (bg_num_df["n"].median() > 10 and bg_num_df["n"].mean() > 20):
        continue
    
    mutation_trend_plot = os.path.join("Plots", f"{area}_mutation_trend.pdf")
    fixation_label_plot = os.path.join("Plots", f"{area}_fixatoin_label.pdf")
    
    logging.info(f"{area} preparing...")
    
    area_fixed_daily_file = os.path.join(AREA_FIXED_DAILY_DIR,
                                         f"{area}_{AVERAGE_PERIOD}_days_average.csv")
    
    if not os.path.exists(area_fixed_daily_file):
        # area_daily = [
        #     {"Date": c_date, **{
        #         mut: mean(mut_info[area].get(d.strftime("%Y-%m-%d"), 0)
        #                   for d in pd.date_range(
        #                       end=c_date,
        #                       periods=AVERAGE_PERIOD
        #                   )) / daily_average
        #         for mut, mut_info in mutation_num.items()
        #         if area in mut_info
        #     }}
        #     for c_date in bg_num
        #     if (daily_average := mean(bg_num.get(d.strftime("%Y-%m-%d"), 0)
        #                               for d in pd.date_range(
        #                                   end=c_date,
        #                                   periods=AVERAGE_PERIOD
        #                               ))) > 20
        # ]
        # area_daily = pd.DataFrame.from_records(area_daily, index="Date")
        with Pool(os.cpu_count()) as p:
            area_daily = p.starmap(
                func=get_mut_percentage,
                iterable=((c_date, AVERAGE_PERIOD, area, bg_num, mutation_num)
                          for c_date in bg_num)
            )
        area_daily = pd.DataFrame.from_records(filter(None, area_daily), index="Date")
        area_daily.index = pd.to_datetime(area_daily.index)
        area_daily = area_daily.sort_index()
        
        area_fixed_daily = area_daily.loc[:, (area_daily > 0.5).sum(axis=0) > 30]
        area_fixed_daily.to_csv(area_fixed_daily_file)
        del area_daily
    else:
        area_fixed_daily = pd.read_csv(area_fixed_daily_file)
        area_fixed_daily["Date"] = pd.to_datetime(area_fixed_daily["Date"])
        area_fixed_daily = area_fixed_daily.set_index("Date")
    
    
    rows = area_fixed_daily.columns.values
    
    x_pos = pd.date_range(
        start=min(area_fixed_daily.index.values),
        end=max(area_fixed_daily.index.values)
    )
    
    fig, axes = plt.subplots(
        nrows=len(rows),
        ncols=1,
        sharex=True,
        sharey=True,
        figsize = (5, 2 * len(rows))
    )
    
    bg = [bg_num[d.strftime("%Y-%m-%d")] for d in x_pos]
    for mut, ax in zip(rows, axes):
        mut_daily = [
            mutation_num[mut][area].get(d.strftime("%Y-%m-%d"), 0)
            for d in x_pos
        ]
        ax.fill_between(x_pos, 0, bg, label="Background", facecolor='#AFDAE8')
        ax.fill_between(x_pos, 0, mut_daily, label = "Mutation", facecolor='#F7E15F')
        ax.tick_params(axis='x', labelrotation=60)
        ax.set_xlim([x_pos[1], x_pos[-1]])
        ax.xaxis.set_major_formatter(DateFormatter('%b %Y'))
        ax.set_ylabel(mut)
        
        
    plt.savefig(mutation_trend_plot, bbox_inches="tight")
    plt.close()

    
    logging.info(f"{area} clustering...")

    clustering = DBSCAN(
        eps=0.5,
        min_samples=15,
        metric="manhattan"
    ).fit(np.array(area_fixed_daily))

    for mut in rows:
        _ = plt.plot(
            area_fixed_daily[mut].index.values,
            area_fixed_daily[mut].values,
            "-o",
            label=mut
        )

    xlim_l, xlim_r = plt.xlim([x_pos[1], x_pos[-1]])
    plt.tick_params(axis='x', labelrotation=60)
    
    labels = pd.DataFrame({
        "Label": clustering.labels_,
        "Area": area
    }, index=area_fixed_daily.index)
    area_labels.append(labels)
    
    n_labels = labels[labels["Label"] != -1]["Label"].nunique()
    logging.info(f"{area} has {n_labels} clusters")


    cluster_colors = {
        i: rgb2hex(c[:3])
        for i, c in enumerate(cm.rainbow(np.linspace(0, 1, n_labels)))
    }
    cluster_colors[-1] = None
    
    all_dates = pd.to_datetime(area_fixed_daily.index.values)
    date_cls = []
    
    start_d = all_dates[0]
    start_l = clustering.labels_[0]
    
    prev_d = all_dates[0]
    prev_l = clustering.labels_[0]
    for curr_d, curr_l in zip(all_dates[1:], clustering.labels_[1:]):
        if curr_l != prev_l:
            date_cls.append((start_d, prev_d, cluster_colors[prev_l]))
            start_d = curr_d
        prev_d, prev_l = curr_d, curr_l
    date_cls.append((start_d, prev_d, cluster_colors[prev_l]))
        
    for start_d, end_d, label_color in date_cls:
        if label_color is not None:
            _ = plt.axvspan(start_d, end_d, alpha=0.3, color=label_color)
    
    plt.savefig(fixation_label_plot, bbox_inches="tight")
    plt.close()

    logging.info(f"{area} done!")

area_labels = pd.concat(area_labels)
area_labels.to_csv(FIXATION_PERIOD_FILE)
logging.info(f"{FIXATION_PERIOD_FILE} saved")
