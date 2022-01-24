import multiprocessing

import mlflow
from tqdm import tqdm

from dataset import emerson_classification_cohort_split
from experiments.fixed_split import main
from motifboost.methods.emerson import EmersonClassifierWithParameterSearch
from motifboost.methods.motif import MotifBoostClassifier
from motifboost.util import human_amino_acids

mlflow.set_experiment("emerson_cohort_split_full")


classifier_dict = {
    "motifboost": MotifBoostClassifier(),
    "emerson": EmersonClassifierWithParameterSearch(emerson_classification_cohort_split.get_class,human_amino_acids),
}

settings_dict = {
    "all": emerson_classification_cohort_split,
}

for setting_prefix, setting in settings_dict.items():
    for classifier_prefix, classifier in tqdm(
        classifier_dict.items(), desc="classifiers"
    ):
        main(
            mlflow_experiment_id="emerson_640",
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
