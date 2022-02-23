import multiprocessing

import mlflow
from tqdm import tqdm

from dataset import emerson_classification_cohort_split
from experiments.fixed_split import main
from motifboost.methods.emerson import EmersonClassifierWithParameterSearch
from motifboost.methods.motif import MotifBoostClassifier
from motifboost.util import human_amino_acids
from motifboost.repertoire import repertoire_dataset_loader, augment_repertoire

mlflow.set_experiment("emerson_cohort_split_full")


setting_prefix = "all"
setting = emerson_classification_cohort_split

classifier_dict = {
    "motif": MotifBoostClassifier(),
    "emerson": EmersonClassifierWithParameterSearch(
        setting.get_class, human_amino_acids, multi_process=6
    ),
}

save_dir = "./data/preprocessed/"
experiment_id = "Emerson"
filter_by_sample_id = emerson_classification_cohort_split.filter_by_sample_id
filter_by_repertoire = emerson_classification_cohort_split.filter_by_repertoire

for sequence_ratio in [0.1, 0.25, 0.5]:
    repertoires = repertoire_dataset_loader(
        save_dir,
        experiment_id,
        filter_by_sample_id,
        filter_by_repertoire,
        multiprocess_mode=True,
        save_memory=True,  # for emerson full
    )
    train_repertoires = [r for r in repertoires if r.sample_id.startswith("HIP")]
    val_repertoires = [r for r in repertoires if not r.sample_id.startswith("HIP")]
    # only sample train_repertoires
    train_repertoires = augment_repertoire(
        train_repertoires, len(train_repertoires), sequence_ratio
    )
    del repertoires
    subsampled_repertoires = train_repertoires + val_repertoires
    for classifier_prefix, classifier in tqdm(
        classifier_dict.items(), desc="classifiers"
    ):
        main(
            mlflow_experiment_id="Sequence Depth",
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
                    setting.experiment_id,
                    setting_prefix,
                    classifier_prefix,
                ]
            ),
            multiprocess_mode=True,
            repertoires=subsampled_repertoires,
        )
