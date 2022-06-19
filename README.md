## About

- This repository is to provide examples of [MotifBoost](https://github.com/hmirin/MotifBoost), a library for robust and data-efficient classification of RepSeq data.
- We provide commands to reproduce the results shown in the figures in the [paper](https://www.biorxiv.org/content/10.1101/2021.09.28.462258v1).
  - Note that the random seeds are not fixed for all the commands, as the paper is about the variance of such randomness, we didn't fix the random seed. 

## Citation

https://www.biorxiv.org/content/10.1101/2021.09.28.462258v1.full

```
@article {Katayama2021.09.28.462258,
	author = {Katayama, Yotaro and Kobayashi, Tetsuya J.},
	title = {MotifBoost: k-mer based data-efficient immune repertoire classification method},
	elocation-id = {2021.09.28.462258},
	year = {2021},
	doi = {10.1101/2021.09.28.462258},
	publisher = {Cold Spring Harbor Laboratory},
	URL = {https://www.biorxiv.org/content/early/2021/10/01/2021.09.28.462258},
	eprint = {https://www.biorxiv.org/content/early/2021/10/01/2021.09.28.462258.full.pdf},
	journal = {bioRxiv}
}
```


# Install

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

### Figure 2

#### For N=640 

Classification for ``Emerson Dataset`` is performed by Burden Method and MotifBoost.
```
python -m examples.emerson_dataset_comparison
```

Results are saved in ``mlruns`` folder. Use mlflow to see the ROC-AUC curve and prediction profile. See ``emerson_cohort_split_full`` project.


#### For N < 640

Use subsampled CSVs in ``data/assets/subsampled/[N]/`` Pass CSVs to the script like this.

```
ls [path to subsampled CSV folder]/*.csv | xargs -Ixxxx python -m examples.emerson-dataset-subsampled xxxx 
```

To run subsampling on your machine, run the script below:
```
python -m subsampler --mode paper-fig1 --train_size 50
```

Subsampled datasets are stored in ``data/subsampled/[timestamp]_[uuid]_[parameters].csv``. 

#### Figure 3

Re-run the command for N=250 two times. You will see two different timestamped results for the same subsampled dataset id. Compare the results.

#### Figure 4

See ``notebooks`` folder.

#### Figure 5

Download the prediction profile of each method from N=640 experiment. Compare it with ```pairplot``` of seaborn.

#### Table 1

Classification of CMV / HIV infection status for ``Huth Dataset`` or ``Heather Dataset``, performed by the methods.

```
python -m examples.heather_huth_dataset_comparison
```

Results are saved in ``mlruns`` folder. Use mlflow to see ROC-AUC curve and prediction profile. See ``heather_alpha_cv``, ``heather_beta_cv`` and ``huth_cv`` project.

Note that the experiments of ``Emerson Dataset`` is taken from the Figure 2.

#### Table 2

Classification of CMV infection status using different datasets to check the generalization of the methods.

```
python -m examples.comparison_across_dataset_emerson_to_huth
python -m examples.comparison_across_dataset_huth_to_emerson
```

Results are saved in ``mlruns`` folder. Use mlflow to see ROC-AUC curve and prediction profile. See ``cross_learning_from_emerson_hip_to_huth`` and ``cross_learning_from_huth_to_emerson_hip`` projects.


#### Table 3

Classification of CMV infection status using ``Emerson dataset`` with the fewer number of sequences.
Replace XX to specify the subsample ratio, the subsample dataset id, and the classifier.

```
python -m sequence_subsampler
python -m examples.sequence_depth_specify --sequence_ratio XXX --trial XX --classifier_prefix XX --n_jobs XX
```

Instead of running the first command, subsampled sequences used in the paper can be downloaded from [here](https://drive.google.com/drive/folders/1fOA-cymWEjyZkrWqVwvJTXeE07No1x_1?usp=sharing).

Results are saved in ``mlruns`` folder. Use mlflow to see ROC-AUC curve and prediction profile. See ``sequence_depth`` project.

#### Table 4

See Figure 2 N=640 (The script also outputs the results for k-mer methods)

#### Table 5

See Figure 4.

#### Table 6

See Figure 4.

#### Table 7

Ablation study of MotifBoost using ``Emerson Dataset`` at N=25 and 640.

```
python -m examples.motifboost_performance_analysis
```

Results are saved in ``mlruns`` folder. Use mlflow to see ROC-AUC curve and prediction profile. See ``motifboost_performance_analysis`` project.


#### DeepRC

For DeepRC, use the command below to create datasets to be used with [the author implementation](https://github.com/ml-jku/DeepRC) for the Figures and Tables above. You may need to customize the training scripts.
```
python -m convert_to_deeprc
python -m convert_to_deeprc_cross_learning
```
