import os
import re
import logging
import logging.config
import json
import datetime
from collections import defaultdict

import pandas as pd


SITESMAPPING_FILE = "Data/sitesMapping.csv"
SURVEILLANCE_FILE = "Data/variant_surveillance.tsv"

MUTATION_PER_SEQ_FILE = "Output/mutation_per_seq.json"
MUTATION_NAMES_FILE = "Output/mutation_names.json"
MUTATION_NUM_FILE = "Output/mutation_num.json"
BACKGROUND_NUM_FILE = "Output/background_num.json"


logging.config.fileConfig("logging.conf")

logging.info("Load data...")

df = pd.read_csv(SURVEILLANCE_FILE, sep="\t", low_memory=False, index_col=0)
logging.info(f"{len(df.index)} in raw data")

df = df[df["Collection date"].str.len() == 10]
logging.info(f"{len(df.index)} has complete date")

df["Collection date"] = pd.to_datetime(df["Collection date"])
df = df[df["Collection date"] > datetime.datetime(2019, 11, 30)]
logging.info(f"{len(df.index)} after 2019/11/30")

df = df[df["Host"] == "Human"]
logging.info(f"{len(df.index)} using human host")

df["Continent"] = df["Location"].str.split(" / ").str[0]
df["Area"] = df["Location"].str.split(" /").str[1].str.strip()

# df = df.head(20)


logging.info("Get all possible mutations...")

seqs_mutations = defaultdict(dict)
mutation_names = defaultdict(list)
for c_date, d_group in df.groupby("Collection date"):
    c_date = c_date.strftime("%Y-%m-%d")
    for area, a_group in d_group.groupby("Area"):
        logging.info(f"{c_date} {area}")
        seqs_mutations_area = {}
        for ac, mut in a_group["AA Substitutions"].iteritems():
            if not pd.isna(mut) and mut != "":
                mut = mut[1:-1].split(",")
                seqs_mutations_area[ac] = mut
                for m in mut:
                    mutation_names[m].append(ac)
        seqs_mutations[c_date][area] = seqs_mutations_area

with open(MUTATION_PER_SEQ_FILE, "w") as f:
    json.dump(seqs_mutations, f)
    logging.info(f"{MUTATION_PER_SEQ_FILE} saved!")


with open(MUTATION_NAMES_FILE, "w") as f:
    json.dump(mutation_names, f)
    logging.info(f"{MUTATION_NAMES_FILE} saved!")


logging.info("Summarize percentage sum...")


mutation_num = defaultdict(dict)
for mut, accessions in mutation_names.items():
    logging.info(mut)
    for area, ac_info in df.loc[accessions].groupby("Area"):
        percentage_daily = dict(
            i for i in ac_info["Collection date"].dt.strftime("%Y-%m-%d").value_counts().iteritems()
        )
        mutation_num[mut][area] = percentage_daily


with open(MUTATION_NUM_FILE, "w") as f:
    json.dump(mutation_num, f)
    logging.info(f"{MUTATION_NUM_FILE} saved!")


logging.info("Calculate daily sampling size...")

globalDates = pd.to_datetime(df["Collection date"].unique())

bgNum = defaultdict(dict)
for continent, group in df.groupby("Area"):
    background = group["Collection date"].value_counts()
    background = background.sort_index()
    logging.info(continent)
    for d in globalDates:
        d_str = d.strftime("%Y-%m-%d")
        if d in background.index:
            bgNum[continent][d_str] = int(background[d])
        else:
            bgNum[continent][d_str] = 0

with open(BACKGROUND_NUM_FILE, "w") as f:
    json.dump(bgNum, f)
    logging.info(f"{BACKGROUND_NUM_FILE} saved!")

logging.info("Done!")
