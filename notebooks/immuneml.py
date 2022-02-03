from pathlib import Path
from typing import List
import tempfile

from motifboost.repertoire import repertoire_dataset_loader, Repertoire
import pandas as pd
from dataset import huth_classification
import immuneML.data_model.repertoire.Repertoire as immumeml_repertoire

from immuneML.encodings.EncoderParams import EncoderParams

from immuneML.environment.LabelConfiguration import LabelConfiguration

from immuneML.environment.Label import Label



import airr
import pandas as pd

from immuneML.IO.dataset_import.DataImport import DataImport
from immuneML.IO.dataset_import.DatasetImportParams import DatasetImportParams
from immuneML.data_model.dataset.Dataset import Dataset
from immuneML.data_model.receptor.ChainPair import ChainPair
from immuneML.data_model.receptor.RegionType import RegionType
from immuneML.data_model.receptor.receptor_sequence.SequenceFrameType import SequenceFrameType
from immuneML.data_model.repertoire.Repertoire import Repertoire
from immuneML.util.ImportHelper import ImportHelper
from scripts.specification_util import update_docs_per_mapping

repertoires = repertoire_dataset_loader(
    "./data/preprocessed/",
    "Huth",
    huth_classification.filter_by_sample_id,
    huth_classification.filter_by_repertoire,
    multiprocess_mode=True,
    save_memory=True,  # for emerson full
)


class TemporaryDirectoryFactory:
    def __init__(
        self,
    ):
        self.dirs: List[Path] = []

    def new(self) -> Path:
        d = Path(tempfile.mkdtemp())
        self.dirs.append(d)
        return d

    def reset(self):
        """delete all directory in dirs"""
        for d in self.dirs:
            d.rmdir()
        self.dirs = []


def save_repertoire_by_immuneml_format(repertoire: Repertoire, dir: Path) -> Path:
    seqs = repertoire.sequences.get_all()
    seqs2 = ["A" * len(s) for s in seqs]
    counts = list(repertoire.counts)
    idxs = list(range(len(seqs)))
    productives = [True for _ in idxs]
    name = repertoire.sample_id
    df = pd.DataFrame.from_dict(
        {
            "sequence_id": idxs,
            "sequence_aas": seqs,
            "sequences": seqs2,
            "counts": counts,
            # "productive": productives,
        }
    )
    pth = dir / f"{name}.tsv"
    df.to_csv(pth, index=False, sep="\t")
    return pth


def save_repertoires_by_immuneml_format(
    repertoires: List[Repertoire], directory: TemporaryDirectoryFactory
) -> Path:
    d = directory.new()
    paths = [save_repertoire_by_immuneml_format(r, d) for r in repertoires]
    subject_ids = [r.sample_id for r in repertoires]
    dic = {}
    for key in repertoires[0].info.keys():
        values = [r.info[key] for r in repertoires]
        dic.update({key: values})
    dic["filename"] = paths
    dic["subject_id"] = subject_ids
    df = pd.DataFrame.from_dict(dic)
    pth = d / "metadata.csv"
    df.to_csv(pth, index=False)
    return d


tdf = TemporaryDirectoryFactory()
saved_path = save_repertoires_by_immuneml_format(repertoires, tdf)
print(saved_path)
del repertoires

"""
from pathlib import Path
#saved_path = Path("/tmp/tmpv2aard10/")
from immuneML.IO.dataset_import import AIRRImport, DatasetImportParams, DataImport
"""
from immuneML.IO.dataset_import import AIRRImport
datasets = AIRRImport.AIRRImport.import_dataset(
    {
        "path": saved_path,
        "metadata_file": saved_path / "metadata.csv",
        "result_path": saved_path,
        "region_type": "IMGT_CDR3",
        "column_mapping": {}
    },
    "Huth",
)


from immuneML.ml_methods.AtchleyKmerMILClassifier import AtchleyKmerMILClassifier
from immuneML.encodings.atchley_kmer_encoding.AtchleyKmerEncoder import (
   AtchleyKmerEncoder,   
)
# AtchleyKmerMILClassifier()

import datetime

print(datetime.datetime.now())
print("encoding...")
ake = AtchleyKmerEncoder.build_object(
    datasets,
    **{
        "k": 4,
        "skip_first_n_aa": 0,
        "skip_last_n_aa": 0,
        "abundance": "relative_abundance",
        "normalize_all_features": False,
    },
)
# TODO:  normalize_all_features / tcrb_relative_abundance ってなに？
encoder_params = EncoderParams(saved_path / "result", LabelConfiguration(labels=[Label("cmv")]),pool_size=12)
ake.encode(datasets,encoder_params)
print(datetime.datetime.now())
print("encoded...")

from IPython import embed

embed()
