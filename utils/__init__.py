import os
import logging
from datetime import datetime

AVERAGE_PERIOD = 14

TARGET_PROTEIN = "Spike"
SAMPLE_END_DATE = datetime(2020, 5, 1)
MUTATION_SCORE = 1
MISSING_PENALTY = 0

DATA_DIR = "data"
OUTPUT_DIR = "output"
PLOTS_DIR = "plots"
LOG_FILE = "run.log"

SITESMAPPING_FILE = os.path.join(DATA_DIR, "sitesMapping.csv")
SURVEILLANCE_FILE = os.path.join(DATA_DIR, "variant_surveillance.tsv")

MUTATION_PER_SEQ_FILE = os.path.join(OUTPUT_DIR, "mutation_per_seq.feather")
MUTATION_NUM_FILE = os.path.join(OUTPUT_DIR, "mutation_num.json")
BACKGROUND_NUM_FILE = os.path.join(OUTPUT_DIR, "background_num.json")

AREA_FIXED_DAILY_DIR = os.path.join(OUTPUT_DIR, "area_fixed_daily")
FIXATION_LINKAGE_FILE = os.path.join(OUTPUT_DIR, "fixation_linkage.csv")

TRAINING_DATA_FILE = os.path.join(OUTPUT_DIR, "training_data.feather")

EMBEDDINGS_SEQ_FILE = os.path.join(OUTPUT_DIR, "embeddings_seq.csv")
EMBEDDINGS_MUT_FILE = os.path.join(OUTPUT_DIR, "embeddings_mut.csv")
MUTATION_SCORES_FILE = os.path.join(OUTPUT_DIR, "mutation_scores.feather")
TRAINING_LOSSES_PLOT = os.path.join(PLOTS_DIR, "training_losses.pdf")

logging.basicConfig(
    filename=LOG_FILE,
    format="[%(asctime)s %(filename)s]: %(message)s",
    datefmt="%Y-%m-%d %I:%M:%S %p",
    level=logging.INFO
)
