
# Usage

## Preparation
Requires Python>=3.8
```
git clone https://github.com/hmirin/motifboost-paper
cd motifboost-paper
pip install -r requirements.txt
```

Download data and preprocess with:
```
bash download.sh
python -m convert
```

## Reproducing the results

### Figure 1

#### For N=640 

Classification for ``Emerson Dataset`` is performed by Burden Method and MotifBoost.
```
python -m examples.emerson_dataset_comparison
```

Results are saved in ``mlruns`` folder. Use mlflow to see ROC-AUC curve and prefiction profile. See ``emerson_cohort_split_full`` project.


#### For N < 640

We need to perform subsampling. 
Create subsampled dataset like below.
Subsampled datasets are stored in ``data/subsampled/[timestamp]_[N_size]_[N_times]/[timestamp]_[N_size]_[N_times]_[id].csv``.
```
python -m subsampler N_size=400 N_times=50 
```
Pass CSVs to the script like this.

```
ls [path to subsampled CSV folder]/*.csv | xargs -Ixxxx python -m examples.emerson-dataset-subsampled xxxx 
```

Results are saved in mlruns folder. Use mlflow to see ROC-AUC curve and prefiction profile.


#### Figure 2

Re-run the command for N=250 two times. You will see two different timestamped results for the same subsampled dataset id. Compare the results.

#### Figure 3

See ``notebooks`` folder.

#### Figure 4

Download the prediction profile of each method from N=640 experiment. Compare it with ```pairplot``` of seaborn.

#### Table 1 (Other datasets)

Classification for ``Huth Dataset`` or ``Heather Dataset`` is performed by Burden Method and MotifBoost.

```
python -m examples.heather_huth_dataset_comparison
```

Results are saved in ``mlruns`` folder. Use mlflow to see ROC-AUC curve and prefiction profile. See ``heather_alpha_cv`` and ``heather_beta_cv`` ``huth_cv`` project.