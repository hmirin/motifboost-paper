# Generate data for Table. X
# Subsample Emerson sequences (at N=640 for DeepRC repertoire and MotifBoost)MotifBoost for 3 times
import os
from typing import Optional

import click
from MotifBoost.motifboost.repertoire import (
    augment_repertoire,
    repertoire_dataset_loader,
)
from tqdm import tqdm

from convert_to_deeprc import convert_to_deeprc
from dataset import emerson_classification_cohort_split


@click.command()
@click.option("--save_dir", default="./data/preprocessed/", help="Path to save dir")
@click.option(
    "--to_dir", default="./data/subsampled_sequence_ratio/", help="Path to save dir"
)
@click.option(
    "--experiment_id", default="Emerson", type=str, help="experiment_id to convert"
)
# @click.option(
#     "--sample_ratio", default=None, type=float, help="experiment_id to convert"
# )
@click.option("--test_str", default="Keck", type=str, help="experiment_id to convert")
@click.option("--times", default=3, type=int, help="experiment_id to convert")
def main(
    save_dir: str,
    to_dir: str,
    experiment_id: str,
    test_str: Optional[str],
    times: int,
    # sample_ratio: float,
):
    for sequence_ratio in tqdm([0.1, 0.01, 0.001], desc="sample ratio"):
        for t in tqdm(range(times), desc="N"):
            repertoires = repertoire_dataset_loader(
                save_dir,
                experiment_id,
                emerson_classification_cohort_split.filter_by_sample_id,
                emerson_classification_cohort_split.filter_by_repertoire,
                multiprocess_mode=True,
                save_memory=False,
            )
            train_repertoires = [
                r for r in repertoires if not r.sample_id.startswith(test_str)
            ]
            val_repertoires = [
                r for r in repertoires if r.sample_id.startswith(test_str)
            ]
            # only sample train_repertoires
            train_repertoires = augment_repertoire(
                train_repertoires, len(train_repertoires), sequence_ratio
            )
            del repertoires
            subsampled_repertoires = train_repertoires + val_repertoires
            del train_repertoires
            del val_repertoires

            to_dir_motif = (
                to_dir + "/" + experiment_id + "_" + str(sequence_ratio) + "_" + str(t)
            )
            os.makedirs(to_dir_motif, exist_ok=True)
            for r in tqdm(subsampled_repertoires, desc="saving repertoire"):
                r.save(to_dir_motif)
            to_dir_deeprc = (
                to_dir
                + "/"
                + experiment_id
                + "_deeprc"
                + "_"
                + str(sequence_ratio)
                + "_"
                + str(t)
            )
            convert_to_deeprc(
                to_dir_motif,
                to_dir_deeprc,
                experiment_id,
                emerson_classification_cohort_split.get_class,
                emerson_classification_cohort_split.filter_by_sample_id,
                emerson_classification_cohort_split.filter_by_repertoire,
            )
            del sampled_repertoires


if __name__ == "__main__":
    main()

# python -m scripts.sequence_subsampler  --to_dir ./data/interim/sampled_repertoires/Emerson/XX/ --times 50 --train_size XX --test_str Keck
