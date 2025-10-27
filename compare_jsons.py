import json
from pathlib import Path
import pandas as pd
from pandas import json_normalize
from deepdiff import DeepDiff
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# --- CONFIG ---
FOLDER = "3C_testdaten_json"  # folder containing all your .json files
OUT_EXCEL = "json_differences.xlsx"
# ---------------

# --- LOAD FILES ---
files = sorted(Path(FOLDER).glob("*.json"))
if not files:
    raise FileNotFoundError(f"No .json files found in {FOLDER}")

data = [json.load(open(f)) for f in files]

# --- FLATTEN JSONS ---
dfs = []
for file, d in zip(files, data):
    flat = json_normalize(d, sep='.')
    flat['source'] = file.name
    dfs.append(flat)

df = pd.concat(dfs, ignore_index=True).set_index('source').T

# --- SHOW ONLY DIFFERENCES ---
diffs = df[df.nunique(axis=1) > 1]
print("\n=== Fields with differences ===")
print(diffs)

# --- SAVE TO EXCEL ---
diffs.to_excel(OUT_EXCEL)
print(f"\nSaved detailed comparison to {OUT_EXCEL}")

# --- PAIRWISE DIFFERENCE HEATMAP ---
def diff_score(a, b):
    return len(DeepDiff(a, b, ignore_order=True))

n = len(data)
matrix = np.zeros((n, n))
for i in range(n):
    for j in range(n):
        matrix[i, j] = diff_score(data[i], data[j])

plt.figure(figsize=(8,6))
sns.heatmap(
    matrix, annot=True, fmt=".0f", cmap="coolwarm",
    xticklabels=[f.name for f in files],
    yticklabels=[f.name for f in files]
)
plt.title("Pairwise JSON Difference Intensity")
plt.tight_layout()
plt.show()

# --- OPTIONAL: FIELD AGREEMENT SCORE ---
flat_dicts = [json_normalize(d, sep='.').to_dict(orient='records')[0] for d in data]
all_keys = set().union(*flat_dicts)
agreement = {}
for key in all_keys:
    values = [fd.get(key) for fd in flat_dicts]
    most_common = pd.Series(values).mode().size / len(values)
    agreement[key] = most_common

agreement_df = pd.DataFrame.from_dict(agreement, orient='index', columns=['agreement_score'])
agreement_df = agreement_df.sort_values(by='agreement_score')

print("\n=== Least consistent fields ===")
print(agreement_df.head(10))