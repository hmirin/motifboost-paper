import os
from typing import Literal

from motifboost.methods.atchley_mil import AtchleyKmerMILClassifier
from motifboost.methods.atchley_simple import AtchleySimpleClassifier
from motifboost.methods.emerson import EmersonClassifierWithParameterSearch
from motifboost.methods.motif import MotifBoostClassifier
from motifboost.repertoire import Repertoire, repertoire_dataset_loader
from motifboost.util import human_amino_acids
from tqdm import tqdm

from dataset import emerson_classification_cohort_split, huth_classification
from experiments.fixed_split import main


def emerson_hip_to_huth_split(x: Repertoire) -> Literal["train", "test", "other"]:
    if "Keck" in x.sample_id:
        return "train"
    elif "unstimulated" in x.sample_id:
        return "test"
    else:
        print(x.sample_id)
        raise NotImplementedError(x)


def huth_to_emerson_hip_split(x: Repertoire) -> Literal["train", "test", "other"]:
    if "Keck" in x.sample_id:
        return "test"
    elif "unstimulated" in x.sample_id:
        return "train"
    else:
        print(x.sample_id)
        raise NotImplementedError(x)


classifier_dict = {
    "motif": MotifBoostClassifier(),
    "emerson": EmersonClassifierWithParameterSearch(
        emerson_classification_cohort_split.get_class,
        human_amino_acids,
        multi_process=4,
    ),
    "atchley_simple": AtchleySimpleClassifier(
        n_gram=3, n_subsample=10000, n_codewords=100, n_augmentation=100, n_jobs=8
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

if __name__ == "__main__":

    save_dir = "./data/preprocessed/"

    emerson_repertoires = repertoire_dataset_loader(
        save_dir,
        "Emerson",
        lambda x: not x.startswith("HIP"),
        emerson_classification_cohort_split.filter_by_repertoire,
        multiprocess_mode=True,
        save_memory=True,
    )
    print("Emerson Keck", len(emerson_repertoires))

    huth_repertoires = repertoire_dataset_loader(
        save_dir,
        "Huth",
        huth_classification.filter_by_sample_id,
        huth_classification.filter_by_repertoire,
        multiprocess_mode=True,
        save_memory=True,
    )
    print("Huth unstimulated", len(emerson_repertoires))
    for r in huth_repertoires:
        r.info["CMV"] = r.info["cmv"]
    repertoires = emerson_repertoires + huth_repertoires

    for classifier_prefix, classifier in tqdm(
        classifier_dict.items(), desc="classifiers"
    ):
        main(
            mlflow_experiment_id="cross_learning_from_huth_to_emerson_hip"
            + os.uname().nodename,
            save_dir=save_dir,
            fig_save_dir="./data/",
            experiment_id="huth_to_emerson_hip",
            get_split=huth_to_emerson_hip_split,
            filter_by_sample_id=None,
            filter_by_repertoire=None,
            get_class=lambda x: x.info["CMV"],
            classifier=classifier,
            prefix="_".join(["huth_to_emerson_hip", classifier_prefix]),
            repertoires=repertoires,
        )
