import multiprocessing
import os
from glob import glob
from itertools import product
from typing import Literal

import pandas as pd
from motifboost.methods.atchley_mil import AtchleyKmerMILClassifier
from motifboost.methods.atchley_simple import AtchleySimpleClassifier
# from motifboost.methods.motif import MotifClassifier
from motifboost.repertoire import Repertoire, repertoire_dataset_loader
from motifboost.util import human_amino_acids
from tqdm import tqdm

# from motifboost.methods.emerson import EmersonClassifierWithParameterSearch
from dataset import emerson_classification_cohort_split
from experiments.fixed_split import main

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

settings_dict = {
    "all": emerson_classification_cohort_split,
}

repertoires = repertoire_dataset_loader(
    save_dir="./data/preprocessed/",
    experiment_id="Emerson",
)

n_processes = multiprocessing.cpu_count()
print("multiprocessing cpu_count", n_processes)

for sample in [100, 250, 400]:
    idx = 0
    for split_file in tqdm(
        sorted(glob("./data/assets/subsampled/" + str(sample) + "/*"))
    ):
        if idx >= 3:
            break
        idx += 1

        def get_split(x: Repertoire) -> Literal["train", "test", "other"]:
            df = pd.read_csv(split_file)
            trainingset_names = list(df[df["type"] == "train"]["sample_name"])
            testset_names = list(df[df["type"] == "test"]["sample_name"])
            # convert to deeprc based naming
            testset_names = [n.replace("_MC1", "") for n in testset_names]
            if x.sample_id in trainingset_names:
                # print("train",x.sample_id)
                return "train"
            elif x.sample_id in testset_names:
                # print("test",x.sample_id)
                return "test"
            else:
                return "other"

        filtered_repertoire = [
            r for r in repertoires if get_split(r) in ["train", "test"]
        ]

        def wrapper(x):
            setting_prefix = x[0][0]
            setting = x[0][1]
            classifier_prefix = x[1][0]
            classifier = x[1][1]
            main(
                mlflow_experiment_id="emerson_cohort_subsample_" + str(sample),
                save_dir="./data/preprocessed/",
                fig_save_dir="./data/",
                experiment_id=setting.experiment_id,
                filter_by_sample_id=setting.filter_by_sample_id,
                filter_by_repertoire=setting.filter_by_repertoire,
                get_class=setting.get_class,
                get_split=get_split,
                classifier=classifier,
                prefix="_".join(
                    [
                        setting.experiment_id,
                        setting_prefix,
                        classifier_prefix,
                        os.path.basename(split_file),
                    ]
                ),
                multiprocess_mode=True,
                repertoires=filtered_repertoire,
            )

        single_process_exps = list(
            product(
                settings_dict.items(),
                [x for x in classifier_dict.items()],
            )
        )
        print("processing single process experiments...")
        list(map(wrapper, single_process_exps))
