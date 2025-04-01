from pathlib import Path
# from sceptr import sceptr
import sceptr
from model import sceptr_unidirectional, load_trained
from tqdm import tqdm
import warnings
import pandas as pd
import torch

warnings.simplefilter("ignore")

evalpath = Path.cwd() / "data" / "alpha"/ "sceptr-eval"
# evalpath = Path.cwd() / "data" / "beta"/ "sceptr-eval"

# i (run) : best_epoch
best_epochs_alpha = {
    0: 49,
    1: 27,
    2: 16,
    3: 11,
    4: 43,
    5: 15,
    6: 35,
    7: 49,
    8: 15,
    9: 20,
}

bestepochs_beta = {
    0: 33,
    1: 49,
    2: 32,
    3: 20,
    4: 49,
    5: 10,
    6: 49,
    7: 43,
    8: 49,
    9: 49,
}

bestepochs = best_epochs_alpha

for i in range(0, 10):
    bestepoch = bestepochs[i]
    path = Path.cwd() / "results-new-alpha" / "sceptr" / f"trained-sceptr-{i}"
    # path = Path.cwd() / "results-new-beta" / "sceptr" / f"trained-sceptr-{i}"

    print(path, ":", bestepoch)

    model = load_trained(
        path / f"Epoch {bestepoch}" / f"classifier-{bestepoch}.pth",
        sceptr_unidirectional
    )
    preds = {
        "preds": [],
        "actual": [],
    }
    for file in tqdm(list(evalpath.glob("*/*.tsv"))):
        df = pd.read_csv(file, sep = "\t")
        embedding = sceptr.calc_vector_representations(df)
        embedding = torch.from_numpy(embedding).cuda() if torch.cuda.is_available() else torch.from_numpy(embedding)
        preds["preds"].append(model(embedding).item())
        preds["actual"].append(1 if "cancer" in str(file) else 0)
    pd.DataFrame(preds).to_csv(path / f"eval-set-auc-{bestepoch}.csv", index = False)
