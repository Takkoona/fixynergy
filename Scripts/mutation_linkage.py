import logging
import json
from statistics import mean
from datetime import timedelta
from collections import defaultdict

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.dates import DateFormatter
from matplotlib import cm
from matplotlib.colors import rgb2hex
from sklearn.cluster import DBSCAN


MUTATION_NUM_FILE = "Output/mutation_num.json"
BACKGROUND_NUM_FILE = "Output/background_num.json"
MUTATION_PER_SEQ_FILE = "Output/mutation_per_seq.json"


TYPED_STRAINS_FILE = "Output/typed_strains.json"

AVERAGE_PERIOD = 14

logging.basicConfig(
    format="[%(asctime)s]: %(message)s",
    datefmt="%Y-%m-%d %I:%M:%S %p",
    level=logging.INFO
)

with open(MUTATION_NUM_FILE) as f:
    mutation_num = json.load(f)
    
with open(BACKGROUND_NUM_FILE) as f:
    background_num = json.load(f)

with open(MUTATION_PER_SEQ_FILE) as f:
    mutation_per_seq = json.load(f)


typed_strains = {
    "dominant": defaultdict(list),
    "recessive": defaultdict(list)
}
for area, bg_num in background_num.items():
    if area != "Australia":
        continue
    
    logging.info(f"{area} preparing...")
    
    area_daily = [
        {"Date": c_date, **{
            mut: mean(mut_info[area].get(d.strftime("%Y-%m-%d"), 0)
                      for d in pd.date_range(end=c_date, periods=AVERAGE_PERIOD)) / daily_average
            for mut, mut_info in mutation_num.items()
            if area in mut_info
        }}
        for c_date in bg_num
        if (daily_average := mean(bg_num.get(d.strftime("%Y-%m-%d"), 0)
                                  for d in pd.date_range(end=c_date, periods=AVERAGE_PERIOD))) > 20
    ]
    area_daily = pd.DataFrame.from_records(area_daily, index="Date")
    area_daily.index = pd.to_datetime(area_daily.index)
    area_daily = area_daily.sort_index()
    
    area_fixed_daily = area_daily.loc[:, (area_daily > 0.5).sum(axis=0) > 30]
    
    rows = area_fixed_daily.columns.values
    
    x_pos = pd.date_range(
        start=min(area_daily.index.values),
        end=max(area_daily.index.values)
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
        
        
    plt.savefig("Plots/test.pdf", bbox_inches="tight")
    plt.close()

    
    logging.info(f"{area} clustering...")

    clustering = DBSCAN(
        eps=0.5,
        min_samples=2,
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
    
    labels = pd.Series(clustering.labels_, index=area_fixed_daily.index)
    n_labels = labels.nunique() - 1
    logging.info(f"{area} has {n_labels} clusters")
    
    for l, group in labels.groupby(labels):
        if l >= 0:
            logging.info(f"{area} {l + 1} / {n_labels}")
            median_freq = area_fixed_daily.loc[group.index.values].median(axis=0)
            dominant_mut = pd.Series(median_freq[median_freq > 0.8].index.values)
            recessive_mut = pd.Series(median_freq[median_freq < 0.2].index.values)
            
            dominant_mut_str = ", ".join(i for i in dominant_mut)
            
            for c_date in group.index.values:
                c_date = pd.to_datetime(c_date).strftime("%Y-%m-%d")
                for ac, mut_names in mutation_per_seq[c_date].get(area, {}).items():
                    if all(dominant_mut.isin(mut_names)):
                        typed_strains["dominant"][dominant_mut_str].append(ac)
                    else:
                        r_m = recessive_mut[recessive_mut.isin(mut_names)].values
                        if len(r_m):
                            r_m = ", ".join(i for i in r_m)
                            typed_strains["recessive"][r_m].append(ac)

    cluster_colors = {
        i: rgb2hex(c[:3])
        for i, c in enumerate(cm.rainbow(np.linspace(0, 1, n_labels)))
    }
    cluster_colors[-1] = None
    
    all_dates = pd.to_datetime(area_daily.index.values)
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
    
    plt.savefig("Plots/test2.pdf", bbox_inches="tight")
    plt.close()

    logging.info(f"{area} done!")
    if area == "Australia":
        break


with open(TYPED_STRAINS_FILE, "w") as f:
    json.dump(typed_strains, f)

