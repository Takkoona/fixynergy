import os
import logging
import logging.config
import json
from statistics import mean
from multiprocessing import Pool

import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.dates import DateFormatter


MUTATION_NUM_FILE = "Output/mutation_num.json"
BACKGROUND_NUM_FILE = "Output/background_num.json"

AREA_FIXED_DAILY_DIR = "Output/Area_fixed_daily"

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
        with Pool(os.cpu_count()) as p:
            area_daily = p.starmap(
                func=get_mut_percentage,
                iterable=((c_date, AVERAGE_PERIOD, area, bg_num, mutation_num)
                          for c_date in bg_num)
            )
        area_daily = pd.DataFrame.from_records(filter(None, area_daily), index="Date")
        area_daily.index = pd.to_datetime(area_daily.index)
        area_daily = area_daily.sort_index()
        
        area_fixed_daily = area_daily.loc[:, (area_daily > 0.5).sum(axis=0) > 7]
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
        ncols=2,
        sharex=True,
        sharey="col",
        figsize = (10, 2 * len(rows))
    )
    
    bg = [bg_num[d.strftime("%Y-%m-%d")] for d in x_pos]
    for mut, (ax, ax2) in zip(rows, axes):
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
        
        for mut2 in rows:
            if mut2 == mut:
                ax2.plot_date(
                    area_fixed_daily[mut2].index.values,
                    area_fixed_daily[mut2].values,
                    ".-",
                )
            else:
                ax2.plot_date(
                    area_fixed_daily[mut2].index.values,
                    area_fixed_daily[mut2].values,
                    "-",
                    alpha=0.5
                )
        ax2.tick_params(axis='x', labelrotation=60)
        ax2.set_xlim([x_pos[1], x_pos[-1]])
        ax2.xaxis.set_major_formatter(DateFormatter('%b %Y'))
        
    plt.savefig(mutation_trend_plot, bbox_inches="tight")
    plt.close()

    logging.info(f"{area} done!")

