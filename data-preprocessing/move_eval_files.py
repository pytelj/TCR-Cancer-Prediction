import csv
from pathlib import Path
import shutil

# Adjust depending on the dataset
FILENAMES = Path("filenames/eval_control_files.csv")
SOURCE_DIR = Path("data/alpha/trimmed/control")
DEST_DIR = Path("data/alpha/trimmed-eval/control")

DEST_DIR.mkdir(parents=True, exist_ok=True)

with open(FILENAMES, mode="r") as f:
    reader = csv.reader(f)
    filenames = [row[0] for row in reader]

# Move files
moved_count = 0
for filename in filenames:
    src_file = SOURCE_DIR / filename
    dest_file = DEST_DIR / filename

    if src_file.exists():
        shutil.move(str(src_file), str(dest_file))
        moved_count += 1
    else:
        print(f"File not found: {src_file}")

print(f"Moved {moved_count} files from {SOURCE_DIR} to {DEST_DIR}.")
