import random
import csv
from pathlib import Path

# adjust depending on the dataset
INPUT_DIR = Path("data/beta/sceptr-traintest/control")
OUTPUT_CSV = Path("data-preprocessing/filenames/beta/eval_control_files.csv")

EVAL_PERCENTAGE = 0.20

all_files = list(INPUT_DIR.glob("*.tsv"))
n_eval = int(len(all_files) * EVAL_PERCENTAGE)
selected = random.sample(all_files, n_eval)

with open(OUTPUT_CSV, mode="w", newline="") as f:
    writer = csv.writer(f)
    for file in selected:
        writer.writerow([file.name])

print(f"Selected {n_eval} files out of {len(all_files)} and saved to {OUTPUT_CSV}")
