import pandas as pd
from pathlib import Path
from tqdm import tqdm
import tidytcells as tt

# Input and output directories
INPUT_DIR = Path("data/alpha/full")
OUTPUT_DIR = Path("data/alpha/sceptr-traintest")

subdirs = ["control", "pbmc_cancer"]

# Ensure output directories exist
for subdir in subdirs:
    (OUTPUT_DIR / subdir).mkdir(parents=True, exist_ok=True)

# Function to clean and filter alpha chains
def clean_alpha_df(df):
    # Filter: only TRA calls and non-empty junctions
    enforce_v = df["v_call"].astype(str).str.startswith("TRA") | df["v_call"].isna()
    enforce_j = df["j_call"].astype(str).str.startswith("TRA") | df["j_call"].isna()
    enforce_cdr3 = df["junction_aa"].notna()
    df = df[enforce_v & enforce_j & enforce_cdr3].copy()

    # Enforce functionality using tidytcells
    df["v_call"] = df["v_call"].apply(lambda x: tt.tr.standardise(x, enforce_functional=True, suppress_warnings=True) if pd.notna(x) else x)
    df["j_call"] = df["j_call"].apply(lambda x: tt.tr.standardise(x, enforce_functional=True, suppress_warnings=True) if pd.notna(x) else x)

    return df

# Convert each alpha file to SCEPTR-compatible format
def convert_and_save_alpha(alpha_file, output_file):
    try:
        alpha_df = pd.read_csv(alpha_file, sep="\t")
        alpha_df = clean_alpha_df(alpha_df)

        merged = {
            "TRAV": alpha_df["v_call"].tolist(),
            "TRAJ": alpha_df["j_call"].tolist(),
            "CDR3A": alpha_df["junction_aa"].tolist(),
            "TRBV": [""] * len(alpha_df),
            "TRBJ": [""] * len(alpha_df),
            "CDR3B": [""] * len(alpha_df),
        }

        pd.DataFrame(merged).to_csv(output_file, sep="\t", index=False)
        print(f"{alpha_file.name} converted and saved.")
    except Exception as e:
        print(f"Error processing {alpha_file.name}: {e}")

# Process all files
for subdir in subdirs:
    input_subdir = INPUT_DIR / subdir
    output_subdir = OUTPUT_DIR / subdir

    for alpha_file in tqdm(list(input_subdir.glob("*.tsv")), desc=f"Processing {subdir}"):
        output_file = output_subdir / alpha_file.name
        convert_and_save_alpha(alpha_file, output_file)

print(f"\nAll alpha files processed and saved in {OUTPUT_DIR}")
