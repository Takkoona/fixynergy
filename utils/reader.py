import pandas as pd

from utils import (
    logging,
    TARGET_PROTEIN,
    TARGET_AREA,
    SAMPLE_END_DATE,
    SAMPLE_START_DATE,
    MUTATION_PER_SEQ_FILE,
    ALL_MUT_SETS_FILE,
    ALL_AA_COMBO_FILE,
)


class MutationPerSeqReader:

    def __init__(self) -> None:
        logging.info("Load mutation per seq")
        df: pd.DataFrame = pd.read_csv(MUTATION_PER_SEQ_FILE)
        df["Date"] = pd.to_datetime(df["Date"])

        self.df = df

    def get_data(self) -> pd.DataFrame:
        return self.df

    def area_filter(self):
        self.df = self.df[self.df["Area"] == TARGET_AREA]
        logging.info(f"{self._mut_seq_info()} for {TARGET_AREA}")

    def protein_filter(self):
        self.df = self.df[self.df["Protein"] == TARGET_PROTEIN]
        logging.info(f"{self._mut_seq_info()} are on {TARGET_PROTEIN}")

    def stop_codon_filter(self):
        self.df = self.df[~self.df["To"].str.contains("stop")]
        logging.info(f"{self._mut_seq_info()} are not stop codon")

    def insertion_filter(self):
        self.df = self.df[~self.df["From"].str.contains("ins")]
        logging.info(f"{self._mut_seq_info()} are not insertion")

    def deletion_filter(self):
        self.df = self.df[~(self.df["To"] == "del")]
        logging.info(f"{self._mut_seq_info()} are not deletion")

    def _mut_seq_info(self):
        mut_n = self.df['Mutation'].nunique()
        seq_n = self.df['Accession'].nunique()
        return f"{mut_n} mutations among {seq_n} seqs"


class AminoAcidComboReader:

    def __init__(self) -> None:
        logging.info("Load amino acid combo")
        self.all_aa_combo: pd.DataFrame = pd.read_csv(ALL_AA_COMBO_FILE)
        all_mut_sets: pd.DataFrame = pd.read_csv(ALL_MUT_SETS_FILE)
        all_mut_sets["Date"] = pd.to_datetime(all_mut_sets["Date"])
        self.all_mut_sets = all_mut_sets

    def before_date_data(self):
        mut_sets = self.all_mut_sets[(self.all_mut_sets["Date"] > SAMPLE_START_DATE) &
                                     (self.all_mut_sets["Date"] < SAMPLE_END_DATE)]
        logging.info(f"{len(mut_sets.index)} sequences before date")
        return self._identical_mutation(mut_sets)

    def after_date_data(self):
        mut_sets = self.all_mut_sets[self.all_mut_sets["Date"]
                                     >= SAMPLE_END_DATE]
        logging.info(f"{len(mut_sets.index)} sequences after date")
        return self._identical_mutation(mut_sets)

    def _identical_mutation(self, mut_sets: pd.DataFrame):
        # Remove sequences with identical mutations
        mut_group: pd.DataFrame
        selected_mut_sets = []
        for _, mut_group in mut_sets.groupby("Mut_set", sort=False):
            mut_group = mut_group.sort_values("Date")
            # Select earliest ac when identical mutations found
            selected_mut_sets.append(mut_group.iloc[0].to_dict())
        selected_mut_sets = pd.DataFrame.from_records(selected_mut_sets)
        logging.info(f"{len(selected_mut_sets.index)} unique sequences")

        # Get amino acid state for all sites by merging with 'all_aa_combo'
        selected_mut_sets = self.all_aa_combo.merge(
            selected_mut_sets, on="Mut_set", how="right")
        selected_mut_sets = selected_mut_sets.drop("Mut_set", axis=1)
        selected_mut_sets["AA"] = selected_mut_sets["Protein"] + "_" + \
            selected_mut_sets["Pos"].astype(str) + selected_mut_sets["To"]
        return selected_mut_sets
