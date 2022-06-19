import os

import click
from motifboost.methods.atchley_mil import AtchleyKmerMILClassifier
from motifboost.methods.atchley_simple import AtchleySimpleClassifier
from motifboost.methods.emerson import EmersonClassifierWithParameterSearch
from motifboost.methods.motif import MotifBoostClassifier
from motifboost.repertoire import repertoire_dataset_loader
from motifboost.util import human_amino_acids

from dataset import emerson_classification_cohort_split
from experiments.fixed_split import main

setting_prefix = "all"
setting = emerson_classification_cohort_split


save_dir = "./data/subsampled_sequence_ratio_fixed"
experiment_id = "Emerson"
filter_by_sample_id = emerson_classification_cohort_split.filter_by_sample_id
filter_by_repertoire = emerson_classification_cohort_split.filter_by_repertoire


@click.command()
@click.option("--sequence_ratio", type=float)
@click.option("--trial", type=int)
@click.option("--classifier_prefix", type=str)
@click.option("--n_jobs", type=int)
def wrapper(sequence_ratio: float, trial: int, classifier_prefix: str, n_jobs: int):
    path = save_dir + "/" + experiment_id + f"_{sequence_ratio}_{trial}"
    subsampled_repertoires = repertoire_dataset_loader(
        path,
        experiment_id,
        filter_by_sample_id,
        filter_by_repertoire,
        multiprocess_mode=True,
        save_memory=True,  # for emerson full
    )
    classifier_dict = {
        "motif": MotifBoostClassifier(n_jobs=n_jobs),
        "emerson": EmersonClassifierWithParameterSearch(
            setting.get_class, human_amino_acids, multi_process=n_jobs
        ),
        "atchley_simple": AtchleySimpleClassifier(
            n_gram=3,
            n_subsample=10000,
            n_codewords=100,
            n_augmentation=100,
            n_jobs=n_jobs,
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
            n_jobs=n_jobs,
        ),
    }
    classifier = classifier_dict[classifier_prefix]
    main(
        mlflow_experiment_id="sequence_depth" + os.uname().nodename,
        save_dir=save_dir,
        fig_save_dir="./results/",
        experiment_id=setting.experiment_id,
        get_split=setting.get_split,
        filter_by_sample_id=filter_by_sample_id,
        filter_by_repertoire=filter_by_repertoire,
        get_class=setting.get_class,
        classifier=classifier,
        prefix="_".join(
            [
                str(sequence_ratio),
                str(trial),
                setting.experiment_id,
                setting_prefix,
                classifier_prefix,
            ]
        ),
        multiprocess_mode=True,
        repertoires=subsampled_repertoires,
    )


if __name__ == "__main__":
    wrapper()
