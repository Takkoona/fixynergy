import pandas as pd

from utils import (
    logging,
    TARGET_PROTEIN,
    TARGET_AREA,
    WILD_TYPE_SEQ_FILE,
    MUTATION_PER_SEQ_FILE,
)


class MutationPerSeqReader:

    def __init__(self) -> None:
        logging.info("Load wild type seq")
        wt: pd.DataFrame = pd.read_csv(WILD_TYPE_SEQ_FILE)
        wt["Date"] = pd.to_datetime(wt["Date"])
        self.wt = wt

        logging.info("Load mutation per seq")
        df: pd.DataFrame = pd.read_csv(MUTATION_PER_SEQ_FILE)
        df["Date"] = pd.to_datetime(df["Date"])
        self.df = df

    def get_data(self) -> pd.DataFrame:
        return self.df

    def get_wt(self) -> pd.DataFrame:
        return self.wt

    def area_filter(self):
        self.wt = self.wt[self.wt["Area"] == TARGET_AREA]
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
        wt_n = self.wt["Accession"].nunique()

        return f"{mut_n} mutations among {seq_n} seqs and {wt_n} wild type seqs"
