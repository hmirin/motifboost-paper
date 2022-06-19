import multiprocessing

import mlflow
from dataset import emerson_classification_cohort_split
from experiments.fixed_split import main
from motifboost.methods.atchley_mil import AtchleyKmerMILClassifier
from motifboost.methods.atchley_simple import AtchleySimpleClassifier
from motifboost.methods.emerson import EmersonClassifierWithParameterSearch
from motifboost.methods.motif import MotifBoostClassifier
from motifboost.util import human_amino_acids
from tqdm import tqdm

mlflow.set_experiment("emerson_cohort_split_full")


classifier_dict = {
    "motifboost": MotifBoostClassifier(),
    "emerson": EmersonClassifierWithParameterSearch(
        emerson_classification_cohort_split.get_class, human_amino_acids
    ),
    "atchley_mil": AtchleyKmerMILClassifier(
        target_label="CMV",
        iteration_count=100,
        threshold=0.001,
        evaluate_at=1000,
        use_early_stopping=True,
        random_seed=0,
        learning_rate=0.01,
        zero_abundance_weight_init=True,
        n_jobs=8,
    ),
    "atchley_simple": AtchleySimpleClassifier(
        n_gram=3, n_subsample=10000, n_codewords=100, n_augmentation=100, n_jobs=8
    ),
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
