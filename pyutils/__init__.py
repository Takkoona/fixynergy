import os
import logging
from datetime import datetime


DATA_DIR = "data"
OUTPUT_DIR = "output"
WEBDATA_DIR = "webdata"

if not os.path.exists(OUTPUT_DIR):
    os.mkdir(OUTPUT_DIR)

if not os.path.exists(WEBDATA_DIR):
    os.mkdir(WEBDATA_DIR)

# For processing raw data
ORIGIN_DATE = datetime(2019, 11, 30)
MIN_MUT_FREQ = 10

SURVEILLANCE_FILE = os.path.join(DATA_DIR, "variant_surveillance.tsv")

WILD_TYPE_SEQ_FILE = os.path.join(OUTPUT_DIR, "wild_type_seq.csv")
MUTATION_PER_SEQ_FILE = os.path.join(OUTPUT_DIR, "mutation_per_seq.csv")
SUS_MUTATION_PER_SEQ_FILE = os.path.join(OUTPUT_DIR, "sus_mutation_per_seq.csv")

# For target protein
TARGET_PROTEIN = "Spike"

TARGET_PROTEIN_DIR = os.path.join(OUTPUT_DIR, TARGET_PROTEIN)

if not os.path.exists(TARGET_PROTEIN_DIR):
    os.mkdir(TARGET_PROTEIN_DIR)

# For target data
TARGET_AREA = "USA"

TARGET_DATA_DIR = os.path.join(TARGET_PROTEIN_DIR, TARGET_AREA)

if not os.path.exists(TARGET_DATA_DIR):
    os.mkdir(TARGET_DATA_DIR)

# For found fixation mutation
AVERAGE_PERIOD = 14
MIN_TOTAL_NUM = 20
FIXATION_PERCENTAGE = 0.5
FIXATION_DAYS_THESHOLD = 7

TOTAL_NUM_FILE = os.path.join(TARGET_DATA_DIR, "total_num.csv")
FIXATION_LINKAGE_FILE = os.path.join(TARGET_DATA_DIR, "fixation_linkage.csv")

# For all found amino acid combinations
ALL_MUT_SETS_FILE = os.path.join(TARGET_DATA_DIR, "all_mut_sets.csv")
ALL_AA_COMBO_FILE = os.path.join(TARGET_DATA_DIR, "all_aa_combo.csv")

# For react rendering
MUT_NODE_FILE = os.path.join(WEBDATA_DIR, f"{TARGET_AREA}_mut_node.json")
MUT_FREQ_FILE = os.path.join(WEBDATA_DIR, f"{TARGET_AREA}_mut_freq.csv")

# For logging
logging.basicConfig(
    filename="run.log",
    format="[%(asctime)s %(process)s]: %(message)s",
    datefmt="%Y-%m-%d %I:%M:%S %p",
    level=logging.INFO
)
