import pandas as pd
from pathlib import Path
from tqdm import tqdm
import tidytcells as tt

# Input and output directories
INPUT_DIR = Path("data/beta/full")
OUTPUT_DIR = Path("data/beta/sceptr-traintest")

subdirs = ["control", "pbmc_cancer"]

# Ensure output directories exist
for subdir in subdirs:
    (OUTPUT_DIR / subdir).mkdir(parents=True, exist_ok=True)

# Function to clean and filter beta chains
def clean_beta_df(df):
    # Filter: only TRB calls and non-empty junctions
    enforce_v = df["v_call"].astype(str).str.startswith("TRB") | df["v_call"].isna()
    enforce_j = df["j_call"].astype(str).str.startswith("TRB") | df["j_call"].isna()
    enforce_cdr3 = df["junction_aa"].notna()
    df = df[enforce_v & enforce_j & enforce_cdr3].copy()

    # Enforce functionality using tidytcells
    df["v_call"] = df["v_call"].apply(lambda x: tt.tr.standardise(x, enforce_functional=True, suppress_warnings=True) if pd.notna(x) else x)
    df["j_call"] = df["j_call"].apply(lambda x: tt.tr.standardise(x, enforce_functional=True, suppress_warnings=True) if pd.notna(x) else x)

    return df

# Convert each beta file to SCEPTR-compatible format
def convert_and_save_beta(beta_file, output_file):
    try:
        beta_df = pd.read_csv(beta_file, sep="\t")
        beta_df = clean_beta_df(beta_df)

        merged = {
            "TRAV": [""] * len(beta_df),
            "TRAJ": [""] * len(beta_df),
            "CDR3A": [""] * len(beta_df),
            "TRBV": beta_df["v_call"].tolist(),
            "TRBJ": beta_df["j_call"].tolist(),
            "CDR3B": beta_df["junction_aa"].tolist(),
        }

        pd.DataFrame(merged).to_csv(output_file, sep="\t", index=False)
        print(f"{beta_file.name} converted and saved.")
    except Exception as e:
        print(f"Error processing {beta_file.name}: {e}")

# Process all files
for subdir in subdirs:
    input_subdir = INPUT_DIR / subdir
    output_subdir = OUTPUT_DIR / subdir

    for beta_file in tqdm(list(input_subdir.glob("*.tsv")), desc=f"Processing {subdir}"):
        output_file = output_subdir / beta_file.name
        convert_and_save_beta(beta_file, output_file)

print(f"\nAll beta files processed and saved in {OUTPUT_DIR}")
