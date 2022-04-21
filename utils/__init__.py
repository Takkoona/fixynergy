import os
import logging
from datetime import datetime, timedelta


DATA_DIR = "data"
OUTPUT_DIR = "output"
PLOTS_DIR = "plots"

if not os.path.exists(OUTPUT_DIR):
    os.mkdir(OUTPUT_DIR)

if not os.path.exists(PLOTS_DIR):
    os.mkdir(PLOTS_DIR)

# For processing raw data
ORIGIN_DATE = datetime(2019, 11, 30)
MIN_MUT_FREQ = 10

SURVEILLANCE_FILE = os.path.join(DATA_DIR, "variant_surveillance.tsv")
MUTATION_PER_SEQ_FILE = os.path.join(OUTPUT_DIR, "mutation_per_seq.csv")
SUS_MUTATION_PER_SEQ_FILE = os.path.join(OUTPUT_DIR, "sus_mutation_per_seq.csv")

# For target protein
TARGET_PROTEIN = "Spike"

TARGET_PROTEIN_DIR = os.path.join(OUTPUT_DIR, TARGET_PROTEIN)
TARGET_PROTEIN_PLOT_DIR = os.path.join(PLOTS_DIR, TARGET_PROTEIN)

if not os.path.exists(TARGET_PROTEIN_DIR):
    os.mkdir(TARGET_PROTEIN_DIR)

if not os.path.exists(TARGET_PROTEIN_PLOT_DIR):
    os.mkdir(TARGET_PROTEIN_PLOT_DIR)

# For target data
TARGET_AREA = "United Kingdom"

TARGET_DATA_DIR = os.path.join(TARGET_PROTEIN_DIR, TARGET_AREA)
TARGET_DATA_PLOT_DIR = os.path.join(TARGET_PROTEIN_PLOT_DIR, TARGET_AREA)

if not os.path.exists(TARGET_DATA_DIR):
    os.mkdir(TARGET_DATA_DIR)

if not os.path.exists(TARGET_DATA_PLOT_DIR):
    os.mkdir(TARGET_DATA_PLOT_DIR)

# For found fixation mutation
AVERAGE_PERIOD = 14
MIN_TOTAL_NUM = 20
FIXATION_PERCENTAGE = 0.5
FIXATION_DAYS_THESHOLD = 7

FIXATION_LINKAGE_FILE = os.path.join(TARGET_DATA_DIR, "fixation_linkage.csv")

MUTATION_TREND_PLOT = os.path.join(TARGET_DATA_PLOT_DIR, "mutation_trend.pdf")
FIXATION_LABEL_PLOT = os.path.join(TARGET_DATA_PLOT_DIR, "fixatoin_label.pdf")

# For all found amino acid combinations
ALL_MUT_SETS_FILE = os.path.join(TARGET_DATA_DIR, "all_mut_sets.csv")
ALL_AA_COMBO_FILE = os.path.join(TARGET_DATA_DIR, "all_aa_combo.csv")

# For training
SAMPLE_TIME_SPAN = 4
SAMPLE_END_DATE = datetime(2020, 5, 1)
SAMPLE_START_DATE = SAMPLE_END_DATE - timedelta(days=SAMPLE_TIME_SPAN*30)

SAMPLE_DATE_STR = SAMPLE_START_DATE.strftime("%Y%m%d") + "_" + SAMPLE_END_DATE.strftime("%Y%m%d")
TARGET_DATA_SAMPLED_DIR = os.path.join(TARGET_DATA_DIR, SAMPLE_DATE_STR)
TARGET_DATA_SAMPLED_PLOT_DIR = os.path.join(TARGET_DATA_PLOT_DIR, SAMPLE_DATE_STR)

if not os.path.exists(TARGET_DATA_SAMPLED_DIR):
    os.mkdir(TARGET_DATA_SAMPLED_DIR)

if not os.path.exists(TARGET_DATA_SAMPLED_PLOT_DIR):
    os.mkdir(TARGET_DATA_SAMPLED_PLOT_DIR)

TRAINING_DATA_FILE = os.path.join(TARGET_DATA_SAMPLED_DIR, "training_data.feather")
DUMMY_SEQ_NAMES_FILE = os.path.join(TARGET_DATA_SAMPLED_DIR, "dummy_seq_names.json")
MUTATION_SCORES_FILE = os.path.join(TARGET_DATA_SAMPLED_DIR, "mutation_scores.feather")

TRAINING_LOSSES_PLOT = os.path.join(TARGET_DATA_SAMPLED_PLOT_DIR, "training_losses.pdf")

# For finding mutation combination
COMBO_MIN_NUM = 2

RECOMMENDED_MUTATIONS_FILE = os.path.join(TARGET_DATA_SAMPLED_DIR, "recommended_mutations.csv")

FUTURE_COMBO_FILE = os.path.join(TARGET_DATA_SAMPLED_DIR, "future_combo.csv")

# For logging
logging.basicConfig(
    filename="run.log",
    format="[%(asctime)s %(process)s]: %(message)s",
    datefmt="%Y-%m-%d %I:%M:%S %p",
    level=logging.INFO
)
