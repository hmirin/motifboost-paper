import multiprocessing
from glob import glob

import mlflow
import pandas as pd
from dataset import emerson_classification_cohort_split
from experiments.fixed_split import main
from motifboost.methods.atchley_mil import AtchleyKmerMILClassifier
from motifboost.methods.atchley_simple import AtchleySimpleClassifier
from motifboost.methods.emerson import EmersonClassifierWithParameterSearch
from motifboost.methods.motif import MotifBoostClassifier
from motifboost.repertoire import repertoire_dataset_loader
from motifboost.util import human_amino_acids
from tqdm import tqdm

mlflow.set_experiment("emerson_cohort_split_full")


classifier_dict = {
    "motifboost-change-only-linear-regression": MotifBoostClassifier(
        classifier_method="linear_regression", n_jobs=10
    ),
    "motifboost-change-only-linear-regression-no-augment": MotifBoostClassifier(
        classifier_method="linear_regression", augmentation_times=0, n_jobs=10
    ),
    "motifboost-change-only-no-optuna": MotifBoostClassifier(
        classifier_method="lightgbm", n_jobs=10
    ),
    "motifboost-change-only-no-augment": MotifBoostClassifier(
        augmentation_times=0, n_jobs=10
    ),
    "motifboost-change-only-no-augment-no-optuna": MotifBoostClassifier(
        classifier_method="lightgbm", augmentation_times=0, n_jobs=10
    ),
}

setting_prefix = "all"
setting = emerson_classification_cohort_split

# splits
csvs = sorted(glob("./data/assets/subsampled/25/*"))[:5]
print(csvs)

for i in range(5):
    # N=640
    for classifier_prefix, classifier in tqdm(
        classifier_dict.items(), desc="classifiers"
    ):
        print(classifier_prefix)
        main(
            mlflow_experiment_id="motifboost_performance_analysis",
            save_dir="./data/preprocessed/",
            fig_save_dir="./results/",
            experiment_id=setting.experiment_id,
            get_split=setting.get_split,
            filter_by_sample_id=setting.filter_by_sample_id,
            filter_by_repertoire=setting.filter_by_repertoire,
            get_class=setting.get_class,
            classifier=classifier,
            prefix="_".join([setting.experiment_id, setting_prefix, classifier_prefix]),
            multiprocess_mode=True,
        )

    # N=25
    for classifier_prefix, classifier in tqdm(
        classifier_dict.items(), desc="classifiers"
    ):
        print(classifier_prefix)
        main(
            mlflow_experiment_id="motifboost_performance_analysis",
            save_dir="./data/preprocessed/",
            fig_save_dir="./results/",
            experiment_id=setting.experiment_id,
            get_split=setting.get_split,
            filter_by_sample_id=lambda x: x
            in list(pd.read_csv(csvs[i])["sample_name"]),
            filter_by_repertoire=setting.filter_by_repertoire,
            get_class=setting.get_class,
            classifier=classifier,
            prefix="_".join(
                [setting.experiment_id, setting_prefix, classifier_prefix, "N25"]
            ),
            multiprocess_mode=True,
        )
