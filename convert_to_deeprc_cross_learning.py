# Convert datasets for DeepRC for Table X

from multiprocessing import cpu_count
import pathlib
import sys
from typing import Callable
from typing import List
from typing import Literal
from typing import Optional

import click
import pandas as pd
from convert_to_deeprc import convert_to_deeprc

from dataset import emerson_classification_cohort_split
from dataset import (
    heather_classification_alpha,
    heather_classification_beta,
)
from dataset import huth_classification
from motifboost.repertoire import Repertoire, repertoire_dataset_loader


@click.command()
@click.option(
    "--save_dir", default="./data/preprocessed/", help="Path to save dir"
)
@click.option(
    "--to_dir", default="./data/deeprc_repertoires_cross_learning", help="Path to save dir"
)
@click.option(
    "--train_datasets", type=click.Choice(["Emerson_Cohort1", "Emerson_Cohort2", "Huth"]), multiple = True
)
@click.option(
    "--test_datasets", type=click.Choice(["Emerson_Cohort1", "Emerson_Cohort2", "Huth"]), multiple = True
)
def main(
        save_dir: str,
        to_dir: str,
        train_datasets: List[Literal["Emerson_Cohort1", "Emerson_Cohort2", "Huth"]],
        test_datasets: List[Literal["Emerson_Cohort1", "Emerson_Cohort2", "Huth"]],
):
    if type(train_datasets) == str:
        train_datasets = [train_datasets]
    if type(test_datasets) == str:
        test_datasets = [test_datasets]
    use_datasets = list(zip(train_datasets,["train"] * len(train_datasets))) + list(zip(test_datasets,["test"] * len(test_datasets)))
    loader_config = []
    for use_dataset, split in use_datasets:
        if "Huth" == use_dataset:
            loader_config.append(
                {
                    "experiment_id":"Huth",
                    "filter_by_sample_id":huth_classification.filter_by_sample_id,
                    "filter_by_repertoire":huth_classification.filter_by_repertoire,
                    "split": split,
                    "get_class": huth_classification.get_class
                }
            )
        elif "Emerson_Cohort1" == use_dataset:
            loader_config.append(
                {
                    "experiment_id": "Emerson",
                    "filter_by_sample_id":lambda x: x.startswith("HIP"),
                    "filter_by_repertoire":None,
                    "split": split,
                    "get_class": emerson_classification_cohort_split.get_class,
                }
            )
        elif "Emerson_Cohort2" == use_dataset:
            loader_config.append(
                {
                    "experiment_id": "Emerson",
                    "filter_by_sample_id":lambda x: x.startswith("Keck"),
                    "filter_by_repertoire":None,
                    "split": split,
                    "get_class": emerson_classification_cohort_split.get_class,
                }
            )
        else:
            print(ValueError("No such data_type: " + use_dataset))
            sys.exit(1)

    repertoires = []
    get_class_funcs = []
    for lc in loader_config:
        lc_reps = repertoire_dataset_loader(
            save_dir,
            lc["experiment_id"],
            lc["filter_by_sample_id"],
            lc["filter_by_repertoire"],
            skip_after=None,
            n_processes=cpu_count(),
        )
        for r in lc_reps:
            r.info["split"] = lc["split"]
        repertoires.extend(lc_reps)
        get_class_funcs.append(lc["get_class"])
    
    def get_class(r: Repertoire):
        for get_class_func in get_class_funcs:
            try:
                return get_class_func(r)
            except:
                print("Info: exception",r.info,get_class_func)
                continue
        raise

    convert_to_deeprc(
        save_dir,
        to_dir,
        "_".join(train_datasets) + "_to_" + "_".join(test_datasets),
        get_class,
        None,
        None,
        None,
        None,
        repertoires
    )


if __name__ == "__main__":
    main()

# python -m convert_to_deeprc_cross_learning --train_datasets Emerson_Cohort2 --test_datasets Huth --to_dir ./data/deeprc_repertoires_cross_learning
# python -m convert_to_deeprc_cross_learning --train_datasets Huth --test_datasets Emerson_Cohort2 --to_dir ./data/deeprc_repertoires_cross_learning_huth_to_emerson_cohort2
