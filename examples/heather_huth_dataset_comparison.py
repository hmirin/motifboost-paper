import glob

import pandas as pd
from motifboost.methods.emerson import EmersonClassifierWithParameterSearch
from motifboost.methods.motif import MotifBoostClassifier
from motifboost.repertoire import Repertoire
from motifboost.util import human_amino_acids
from tqdm import tqdm

from dataset import (
    heather_classification_alpha,
    heather_classification_beta,
    huth_classification,
)
from experiments.fixed_split import main

settings = {
    "heather_alpha": heather_classification_alpha,
    "heather_beta": heather_classification_beta,
    "huth": huth_classification,
}

for name, setting in settings.items():
    classifier_dict = {
        "motif": MotifBoostClassifier(),
        "emerson": EmersonClassifierWithParameterSearch(
            setting.get_class, human_amino_acids, multi_process=4
        ),
        "atchley_simple": AtchleySimpleClassifier(
            n_gram=3, n_subsample=10000, n_codewords=100, n_augmentation=100
        ),
        "atchley-mil": AtchleyKmerMILClassifier(
            target_label="CMV",
            iteration_count=250000,
            threshold=0.00001,
            evaluate_at=1000,
            use_early_stopping=False,
            random_seed=0,
            learning_rate=0.001,
            zero_abundance_weight_init=True,
            n_jobs=8,
        ),
    }

    for idx, fle in enumerate(
        sorted(tqdm(glob.glob(f"./data/assets/{name}_split_*.csv")))
    ):
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
