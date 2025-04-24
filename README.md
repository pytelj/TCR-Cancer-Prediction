# TCR LLMs for Cancer Prediction (Modified)

This repository is a modified version of [Rudy C. Yuen’s MEng dissertation project](https://github.com/rcwyuen/tcr-cancer-prediction), originally developed at UCL to explore language model-based TCR embeddings for cancer classification.

The current version was developed for a UCL **BSc Computer Science dissertation**, focused on investigating the use of sparse attention-based Multiple Instance Learning (MIL) and pretrained TCR embedding models for cancer classification.

Key extensions and contributions in this version include:
- A custom data preprocessing pipeline (`data-preprocessing/`) for manually supplied alpha and beta chain files.
- Split-by-chain training (alpha and beta chains processed independently).
- Three new interpretability experiments on the SCEPTR model (Section 6.2 of the dissertation).
- Updated results and comparative evaluations for symbolic vs subsymbolic encodings.

> [!WARNING]
> This code has been tested on Linux CentOS (UCL CS lab 105 Computers).  Although it should work on other OS, it is not guaranteed to work perfectly.

---

## Installation

> [!IMPORTANT]
> We developed the code under Python 3.11, and the requirements.txt has been generated in the same environment.  Therefore installing the requirements may not work for Python versions below 3.11.

1. Download this repository
2. Create a Python Environment venv through
   ```python3 -m venv $YOUR-VENV-NAME-HERE$```
3. Activate your virtual environment, and run the following command
   ```python -m pip install -r scripts/requirements.txt```
   if your computer is a Windows Computer, and 
   ```python -m pip install -r scripts/requirements-linux.txt```
   if it is Linux Ubuntu instead.
4. Install SCEPTR via the following command:
   ```python -m pip install sceptr```

> [!NOTE]
> You should install your own version of PyTorch depending on your CUDA version before installing the `requirements.txt`.  You may find instructions of installing PyTorch [here](https://pytorch.org/).

> [!NOTE]
> SCEPTR has been published officially [here](https://arxiv.org/abs/2406.06397v1).

---

## Preparing the Dataset

To process local TCR data files (manually provided), the following scripts are used from the `data-preprocessing/` directory:

#### `data-preprocessing/`
- `select_files_for_eval.py`  
  Randomly selects a subset of patients for evaluation, producing CSV files listing the selected cancer and control files separately for α and β chains.

- `move_eval_files.py`  
  Moves selected evaluation files into a dedicated subdirectory to separate training/test data from evaluation data.

- `convert_to_sceptr_alpha.py` and `convert_to_sceptr_beta.py`  
  Preprocess and clean α/β chain files into the SCEPTR-compatible format. This includes:
  - Filtering for valid V/J gene calls and non-empty CDR3 sequences.
  - Enforcing chain-specific functionality via `tidytcells`.
  - Outputting a 6-column TSV file compatible with SCEPTR (`TRAV`, `TRAJ`, `CDR3A`, `TRBV`, `TRBJ`, `CDR3B`).

Additionally, to compress the data (i.e. removing all data other than V call, J call and CDR3 sequences), you may run
```
python utils/file-compressor.py
```

#### Evaluation and Train/Test Set Splits

The evaluation and training/test patient files are listed in the `data-preprocessing/filenames/` directory.

Each subdirectory contains `.csv` files specifying the filenames for $\alpha$ and $\beta$ chain data, grouped by class (control vs cancer) and by usage split (train/test vs evaluation):

- [`data-preprocessing/filenames/alpha/`](data-preprocessing/filenames/alpha/)
  - [`eval_control_files.csv`](data-preprocessing/filenames/alpha/eval_control_files.csv)
  - [`eval_pbmc_cancer_files.csv`](data-preprocessing/filenames/alpha/eval_pbmc_cancer_files.csv)
  - [`traintest_control_files.csv`](data-preprocessing/filenames/alpha/traintest_control_files.csv)
  - [`traintest_pbmc_cancer_files.csv`](data-preprocessing/filenames/alpha/traintest_pbmc_cancer_files.csv)

- [`data-preprocessing/filenames/beta/`](data-preprocessing/filenames/beta/)
  - [`eval_control_files.csv`](data-preprocessing/filenames/beta/eval_control_files.csv)
  - [`eval_pbmc_cancer_files.csv`](data-preprocessing/filenames/beta/eval_pbmc_cancer_files.csv)
  - [`traintest_control.csv`](data-preprocessing/filenames/beta/traintest_control.csv)
  - [`traintest_pbmc_cancer_files.csv`](data-preprocessing/filenames/beta/traintest_pbmc_cancer_files.csv)

Evaluation set filenames were randomly selected using `select_files_for_eval.py`.

---

## Downloading TCR-BERT and SCEPTR Models

### Downloading TCR-BERT

To download the two variants of [TCR-BERT](https://www.biorxiv.org/content/10.1101/2021.11.18.469186v1), you may run the following command:

```
python loaders/load_tcrbert.py -o model
```

### Downloading SCEPTR

Please refer to [this](https://pypi.org/project/sceptr/) link for installation instructions for SCEPTR.

---

## Training Classifiers

There are 3 training scripts, where `trainer-sceptr.py` trains a classifier that uses SCEPTR to encode TCRs, `trainer-symbolic.py` trains a classifier that takes in TCRs encoded by physico-chemical properties and `trainer-tcrbert.py` trains a classifier that uses TCR-BERT to encode TCRs.

All of these 3 scripts would need to take in a configuration file, which can be generated by 

```
python trainer.py --make --end
```

after replacing `trainer.py` with the appropriate training script.  If you would want to run training using the default settings, you can run the following command instead.

```
python trainer.py --make
```

All scripts will generate a log file for its training process.  You may change the log file's name with the following command.

```
python trainer.py --log-file custom-filename.log
```

### Training Configurations

To modify the training configurations, you may modify the config.json generated from the command above.  The configurations available for each of the 3 training scripts are different.  You may find the description for each field in each training script as below:

- `trainer-sceptr.py`: [Descriptions Here](instructions/sceptr-config.md)
- `trainer-tcrbert.py`: [Descriptions Here](instructions/tcrbert-config.md)
- `trainer-symbolic.py`: [Descriptions Here](instructions/symbolic-config.md)

To specify which configuration file to run, you may use the following command:

```
python trainer.py -c custom-configs.json
```

> [!TIP]
> When you run multiple training instances and would like to check the progress of each training instance, you can run the following command to check.
> 
> ```
> python for-ssh/checkdone.py
> ```
> 
> It also tells you the time that the training has been stale for.  It is recommended that you check the training instance if it has been stale for over 2 hours.

---

## Analysing Training Instances

The original results from Rudy’s MEng project are retained under `results/` for reference and comparison. All new experiments performed as part of this BSc dissertation—covering both $\alpha$ and $\beta$ chain models—are located in `results-new-alpha/` and `results-new-beta/`.


### Usage of the Evaluation Set

To test a model's performance on the evaluation set, you may use the following command after amending the model's directory and the best performing epoch.

```
python src/calculate_evals.py
```

### Jupyter Notebooks

This repository includes several Jupyter notebooks to analyse training behaviour and interpret model predictions. Key notebooks include:

- [`training-stats-analysis.ipynb`](training-stats-analysis.ipynb): Generates the loss, accuracy and AUC graphs for *one* training instance.
- [`training-stats-combined.ipynb`](training-stats-combined.ipynb): Generates the loss, accuracy and AUC graphs for a series of training instances.
- [`training-stats-combined-alpha-vs-beta.ipynb`](training-stats-combined-alpha-vs-beta.ipynb) **(new)**: Extension of the above to directly compare $\alpha$ and $\beta$ models on the same plots.
- [`eval-stats-combined.ipynb`](eval-stats-combined.ipynb): Generates the confusion matrix and AUC curves for the models that are trained under a 3-way split.
- [`training-stats-tables.ipynb`](training-stats-tables.ipynb) **(new)**: Produces tables summarising accuracy, loss, and AUC on training and test sets across all runs and embeddings.
- [`sceptr-highweight-tcr-analysis.ipynb`](sceptr-highweight-tcr-analysis.ipynb) **(new)**: Identifies high-attention TCRs that recur across cancer patients in the evaluation set.
- [`sceptr-vector-alignment.ipynb`](sceptr-vector-alignment.ipynb) **(new)**: Computes cosine similarity and angle between scoring and classifying layer vectors, both within and across runs.
- [`sceptr-umap-visualisation.ipynb`](sceptr-umap-visualisation.ipynb) **(new)**: Visualises patient-level bag embeddings in 2D using UMAP, showing class separation.

---

Modifications and additions (c) 2025 Jan Pytel

This project builds upon the original work by [RcwYuen](https://github.com/RcwYuen/TCR-Cancer-Prediction) and is used for academic research purposes. The modifications remain under the same MIT License.
