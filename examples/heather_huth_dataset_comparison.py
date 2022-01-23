import argparse
import glob

import mlflow
import pandas as pd
from tqdm import tqdm

from dataset.settings import (
    heather_classification_alpha,
    heather_classification_beta,
    huth_classification,
)
from experiments.fixed_split import main
from motifboost.methods.emerson import EmersonClassifierWithParameterSearch
from motifboost.methods.motif import MotifBoostClassifier
from motifboost.repertoire import Repertoire
from motifboost.util import human_amino_acids

settings = {
    "heather_alpha": heather_classification_alpha,
    "heather_beta": heather_classification_beta,
    "huth": huth_classification
}

for name, setting in settings.items():
    classifier_dict = {
        "motif": MotifBoostClassifier(),
        "emerson": EmersonClassifierWithParameterSearch(
            setting.get_class, human_amino_acids, multi_process=5
        ),
    }

    for idx, fle in enumerate(sorted(tqdm(glob.glob(f"./data/assets/{name}_split_*.csv")))):
        print(idx, fle)
        # create get_class
        df = pd.read_csv(fle)

        def get_split(r: Repertoire):
            if len(df[df["sample_name"] == r.sample_id]) == 1:
                return df[df["sample_name"] == r.sample_id].iloc[0]["type"]
            else:
                raise

        for classifier_prefix, classifier in tqdm(
            classifier_dict.items(), desc="classifiers"
        ):
            main(
                save_dir="./data/preprocessed/",
                fig_save_dir="./data/",
                experiment_id=setting.experiment_id,
                filter_by_sample_id=setting.filter_by_sample_id,
                filter_by_repertoire=setting.filter_by_repertoire,
                get_class=setting.get_class,
                get_split=get_split,
                classifier=classifier,
                prefix=f"{classifier_prefix}_{idx}",
                mlflow_experiment_id=f"{name}_cv",
            )
