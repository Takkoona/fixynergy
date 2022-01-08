import logging
import logging.config
import json
import datetime
from collections import defaultdict

import pandas as pd


WRITE_OUTPUT = True

SITESMAPPING_FILE = "Data/sitesMapping.csv"
SURVEILLANCE_FILE = "Data/variant_surveillance.tsv"

MUTATION_PER_SEQ_FILE = "Output/mutation_per_seq.feather"
MUTATION_NUM_FILE = "Output/mutation_num.json"
BACKGROUND_NUM_FILE = "Output/background_num.json"

if WRITE_OUTPUT:
    logging.config.fileConfig("logging.conf")

logging.info("Load data...")

df: pd.DataFrame = pd.read_csv(
    SURVEILLANCE_FILE,
    sep="\t",
    low_memory=False,
    index_col=0,
    nrows=None if WRITE_OUTPUT else 20
)
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


logging.info("Get all possible mutations...")

seqs_mutations = []
mutation_names = defaultdict(list)
d: pd.Timestamp
d_group: pd.DataFrame
a_group: pd.DataFrame
for d, d_group in df.groupby("Collection date"):
    c_date = d.strftime("%Y-%m-%d")
    for area, a_group in d_group.groupby("Area"):
        logging.info(f"{c_date} {area}")
        for ac, mut, pango in a_group[["AA Substitutions", "Pango lineage"]].itertuples():
            if not pd.isna(mut) and mut != "":
                mut = mut[1:-1]
                if mut:
                    mut = mut.split(",")
                else:
                    mut = ()
            else:
                mut = ()
            for m in mut:
                mutation_names[m].append(ac)
                seqs_mutations.append({
                    "Accession": ac,
                    "Date": d,
                    "Mutation": m,
                    "Lineage": pango
                })


if WRITE_OUTPUT:

    seqs_mutations: pd.DataFrame = pd.DataFrame.from_records(seqs_mutations)
    seqs_mutations.to_feather(MUTATION_PER_SEQ_FILE, index=False)
    logging.info(f"{MUTATION_PER_SEQ_FILE} saved!")


logging.info("Summarize percentage sum...")


mutation_num = defaultdict(dict)
ac_info: pd.DataFrame
for mut, accessions in mutation_names.items():
    logging.info(mut)
    for area, ac_info in df.loc[accessions].groupby("Area"):
        c_dates: pd.Series = ac_info["Collection date"].dt.strftime("%Y-%m-%d")
        percentage_daily = dict(
            i for i in c_dates.value_counts().iteritems()
        )
        mutation_num[mut][area] = percentage_daily

if WRITE_OUTPUT:

    with open(MUTATION_NUM_FILE, "w") as f:
        json.dump(mutation_num, f)
        logging.info(f"{MUTATION_NUM_FILE} saved!")


logging.info("Calculate daily sampling size...")

globalDates = pd.to_datetime(df["Collection date"].unique())

bgNum = defaultdict(dict)
group: pd.DataFrame
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

if WRITE_OUTPUT:

    with open(BACKGROUND_NUM_FILE, "w") as f:
        json.dump(bgNum, f)
        logging.info(f"{BACKGROUND_NUM_FILE} saved!")

logging.info("Done!")
