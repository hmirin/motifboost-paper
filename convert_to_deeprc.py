import pathlib
from typing import Callable, List, Literal, Optional

import click
import pandas as pd
from motifboost.repertoire import Repertoire, repertoire_dataset_loader

from dataset import (
    emerson_classification_cohort_split,
    heather_classification_alpha,
    heather_classification_beta,
    huth_classification,
)


def convert_to_deeprc(
    save_dir: str,
    to_dir: str,
    experiment_id: str,
    get_split: Callable[[Repertoire], Literal["train", "test", "other"]],
    filter_by_sample_id: Optional[Callable[[str], bool]] = None,
    filter_by_repertoire: Optional[Callable[[Repertoire], bool]] = None,
    skip_after: Optional[int] = None,
    n_processes: Optional[int] = None,
    repertoires=None,
):
    if not repertoires:
        repertoires = repertoire_dataset_loader(
            save_dir,
            experiment_id,
            filter_by_sample_id,
            filter_by_repertoire,
            skip_after,
            n_processes=n_processes,
        )

    to_dir_path = pathlib.Path(to_dir) / experiment_id
    to_dir_path.mkdir(parents=True, exist_ok=True)
    metadata_path = to_dir_path / "metadata.tsv"
    pd.DataFrame.from_dict(
        {
            "ID": [r.sample_id for r in repertoires],
            "status": [get_split(r) for r in repertoires],
        }
    ).to_csv(metadata_path, sep="\t")

    for r in repertoires:
        repertoire_path = to_dir_path / "repertoires"
        repertoire_path.mkdir(parents=True, exist_ok=True)
        tsv_path = repertoire_path / (r.sample_id + ".tsv")
        pd.DataFrame.from_dict(
            {"amino_acid": r.sequences.get_all(), "templates": r.counts}
        ).to_csv(tsv_path, sep="\t")


@click.command()
@click.option(
    "--save_dir", default="./data/interim/repertoires", help="Path to save dir"
)
@click.option(
    "--to_dir", default="./data/interim/deeprc_repertoires", help="Path to save dir"
)
@click.option(
    "--experiment_ids", default=[], multiple=True, help="experiment_id to convert"
)
@click.option(
    "--data_type", type=click.Choice(["HeatherAlpha", "HeatherBeta", "Huth", "Emerson"])
)
def main(
    save_dir: str,
    to_dir: str,
    experiment_ids: List[str],
    data_type: Literal["HeatherAlpha", "HeatherBeta", "Huth", "Emerson"],
):
    if not experiment_ids:
        experiment_ids = data_type = ["HeatherAlpha", "HeatherBeta", "Huth", "Emerson"]
    else:
        data_type = [data_type] * len(experiment_ids)

    for experiment_id, _data_type in zip(experiment_ids, data_type):
        if _data_type == "HeatherAlpha":
            experiment_id = "Heather"
            get_class = heather_classification_alpha.get_class
            filter_by_sample_id = heather_classification_alpha.filter_by_sample_id
            filter_by_repertoire = heather_classification_alpha.filter_by_repertoire
        if _data_type == "HeatherBeta":
            experiment_id = "Heather"
            get_class = heather_classification_beta.get_class
            filter_by_sample_id = heather_classification_beta.filter_by_sample_id
            filter_by_repertoire = heather_classification_beta.filter_by_repertoire
        elif _data_type == "Huth":
            get_class = huth_classification.get_class
            filter_by_sample_id = huth_classification.filter_by_sample_id
            filter_by_repertoire = huth_classification.filter_by_repertoire
        elif _data_type == "Emerson":
            get_class = emerson_classification_cohort_split.get_class
            filter_by_sample_id = (
                emerson_classification_cohort_split.filter_by_sample_id
            )
            filter_by_repertoire = (
                emerson_classification_cohort_split.filter_by_repertoire
            )
        else:
            print(ValueError("No such data_type: " + _data_type))
            continue

        convert_to_deeprc(
            save_dir,
            to_dir,
            experiment_id,
            get_class,
            filter_by_sample_id,
            filter_by_repertoire,
            None,
            None,
        )


if __name__ == "__main__":
    main()

# 25, 50, 100, 250, 400
