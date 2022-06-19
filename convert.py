import glob
import logging
import os
import random
import re

import click
import pandas as pd
from motifboost.repertoire import Repertoire
from tqdm import tqdm

_logger = logging.getLogger(__name__)


def convert_Emerson_to_repertoire(data_folder: str, asset_folder: str, save_dir: str):
    # sample informations
    cohort_1_df = pd.read_excel(
        asset_folder + "/emerson_sample_information.xlsx", sheet_name="Cohort 1"
    )
    cohort_2_df = pd.read_excel(
        asset_folder + "/emerson_sample_information.xlsx", sheet_name="Cohort 2"
    )
    cohort_1_df = cohort_1_df.dropna(axis=1, how="all")
    cohort_2_df = cohort_2_df.dropna(axis=1, how="all")
    sample_info_df = pd.concat([cohort_1_df, cohort_2_df])
    sample_info_df = sample_info_df[
        [c for c in sample_info_df.columns if "Inferred" not in c]
    ]
    files = set(glob.glob(data_folder + "/*.tsv"))

    for _, row in tqdm(sample_info_df.iterrows(), total=len(sample_info_df)):
        print(row)
        cmv_status = row["Known CMV status"]
        subject_id = row["Subject ID"]
        if cmv_status not in ["+", "-"]:
            print(
                "This subject has unknown CMV status:", row["Subject ID"], "Skipping..."
            )
            continue

        matched_file = None
        for f in files:
            if subject_id in f:
                matched_file = f
                files = files - set(f)

        if matched_file is None:
            print(
                "This subject has no data available:", row["Subject ID"], "Skipping..."
            )
            continue

        df = pd.read_csv(matched_file, sep="\t")
        df = df.dropna(axis=1, how="all")
        df = df[df["frame_type"] == "In"]

        # TODO: referring the conversion method of XXX
        count_column = "reads"
        if count_column not in df.columns:
            count_column = "templates"
        count_df = df[["amino_acid", count_column]]
        count_df = count_df.groupby("amino_acid").agg(sum).reset_index()
        r = Repertoire(
            experiment_id="Emerson",
            sample_id=subject_id,
            info={
                "CMV": cmv_status == "+",
                "person_id": subject_id,
                "sex": row["Sex"],
                "Age": row["Age"],
                "Race and Ethnicity": row[
                    "Race and ethnicity "
                ],  # trailing space is necessary
                "HLA alleles": row["Known HLA alleles"],
            },
            sequences=list(count_df["amino_acid"]),
            counts=list(count_df[count_column]),
        )
        r.save(save_dir)


def convert_Heather_to_repertoire(data_folder: str, save_dir: str):
    files = glob.glob(data_folder + "/*.dcrcdr3")
    for f in files:
        print(f)
        if "CD" in f:
            print("skipped")
            continue
        m = re.match(r".*(alpha|beta)_(HV|P)(\d+)v(\d)*", f)
        if m is None:
            m = re.match(r".*(alpha|beta)_(HV|P)(\d+)(\d+)*", f)
            if m is None:
                print("skipped")
                continue
        chain, status, person_number, version = m.groups()

        df = pd.read_csv(
            f,
            names=[
                "decombinator_index_1",
                "decombinator_index_2",
                "decombinator_index_3",
                "decombinator_index_4",
                "seq",
                "counts",
            ],
        )
        df.seq.str.split(":")
        df[["inserted", "amino_acids"]] = df["seq"].str.split(":", 1, expand=True)
        df = df[["amino_acids", "counts"]]
        df = df.groupby("amino_acids").agg(sum).reset_index()
        r = Repertoire(
            experiment_id="Heather",
            sample_id=os.path.basename(f).split(".")[0],
            info={
                "filename": os.path.basename(f),
                "HIV": status == "P",
                "treated": version == "2",
                "chain": chain,
                "person_id": status + person_number,
            },
            sequences=list(df["amino_acids"]),
            counts=list(df["counts"]),
        )
        r.save(save_dir)


def convert_Huth_to_repertoire(data_folder: str, save_dir: str):
    files = glob.glob(data_folder + "/*unstim*")
    for f in tqdm(files):
        print(f)
        df = pd.read_csv(f, sep="\t")
        person_id = df["Donor"].iloc[0]
        cmv_positive = False
        if "CMV positive" == df["Serostatus"].iloc[0]:
            cmv_positive = True
        cell_type = "all"
        if "CD8" in df["Cell.type"].iloc[0]:
            cell_type = "CD8-enriched"

        count_df = df[["CDR3.sequence", "Read.count"]]
        count_df = count_df.groupby("CDR3.sequence").agg(sum).reset_index()

        r = Repertoire(
            experiment_id="Huth",
            sample_id=person_id + "_" + cell_type + "_unstimulated",
            info={
                "cmv": cmv_positive,
                "cell_type": cell_type,
                "person_id": person_id,
            },
            sequences=list(count_df["CDR3.sequence"]),
            counts=list(count_df["Read.count"]),
        )
        r.save(save_dir)


def make_test_dataset(save_dir: str):
    # make 10 people dataset
    # 6 positive / 4 negative
    for i in range(10):
        positive = i < 6
        if positive:
            aas = ["A", "W", "K"]
        else:
            aas = ["A", "K"]
        sequences = [
            "".join(random.choices(aas, k=random.randint(5, 10))) for _ in range(100)
        ]
        counts = [random.randint(1, 10) for _ in range(100)]
        r = Repertoire(
            experiment_id="Test",
            sample_id="TestPatient_" + str(i),
            info={
                "positive": positive,
                "person_id": "TestPatient_" + str(i),
            },
            sequences=sequences,
            counts=counts,
        )
        r.save(save_dir)


@click.command()
@click.option("--save_dir", default="./data/preprocessed/", help="Path to save dir")
@click.option("--test", is_flag=True, help="Path to save dir")
def main(save_dir: str, test: bool):
    if test:
        print("generating fake classification dataset")
        make_test_dataset(save_dir)
    else:
        convert_Emerson_to_repertoire(
            "./data/interim/emerson-2017-natgen/",
            "./data/assets/",
            save_dir,
        )
        convert_Heather_to_repertoire(
            "./data/interim/heather-2016-frontimmunol/",
            save_dir,
        )
        convert_Huth_to_repertoire(
            "./data/interim/huth-2018-jimmunol/",
            save_dir,
        )


if __name__ == "__main__":
    main()
