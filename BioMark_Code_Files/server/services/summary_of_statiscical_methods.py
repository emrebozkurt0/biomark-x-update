import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import os
import re

# Get parameters from command line
data_path = sys.argv[1]  # File path
feature_count = int(sys.argv[2]) if len(sys.argv) > 2 else 20  # Number of miRNAs to display

# Optional class pair, csv path, and aggregation label parameters
class_pair = sys.argv[3] if len(sys.argv) > 3 else None  # Class pair (optional)
csv_path = sys.argv[4] if len(sys.argv) > 4 else None  # CSV file path (optional)
agg_label = sys.argv[5] if len(sys.argv) > 5 else ""  # Aggregation label (optional)

# Map short aggregation method codes to human-readable names
_METHOD_NAME_MAP = {
    'rrf': 'Reciprocal Rank Fusion',
    'rank_product': 'Rank Product',
    'weighted_borda': 'Weighted Borda Count',
    'sum': 'Simple Sum',
}

def _humanize_agg_label(label: str) -> str:
    """Convert an aggregation label into a human-readable form.

    Expected formats coming from the server:
      - "method=rrf,k=60"
      - "method=weighted_borda,weights={...}"
    Also be robust to legacy/short forms like just "rrf".
    """
    if not label:
        return ""

    s = str(label).strip()
    low = s.lower()

    # If it's just the bare method token, expand directly
    if low in _METHOD_NAME_MAP:
        return _METHOD_NAME_MAP[low]

    # Otherwise parse comma-separated key=value pairs, replacing method value
    try:
        parts = [p.strip() for p in re.split(r"\s*,\s*", s) if p.strip()]
    except Exception:
        parts = [s]

    out_parts = []
    method_seen = False
    for p in parts:
        m = re.match(r"(?i)^method\s*=\s*(.+)$", p)
        if m:
            method_seen = True
            val = m.group(1).strip().lower()
            readable = _METHOD_NAME_MAP.get(val, m.group(1).strip())
            # Prefer to show method name alone (without the "method=" prefix)
            out_parts.append(readable)
        else:
            out_parts.append(p)

    # If no explicit method= was present but the string starts with a known token, expand best-effort
    if not method_seen:
        maybe = parts[0].lower()
        if maybe in _METHOD_NAME_MAP:
            parts[0] = _METHOD_NAME_MAP[maybe]
            return ", ".join([parts[0]] + parts[1:])

    return ", ".join(out_parts)

# Extract analysis name from data_path (remove 'uploads/' and .csv extension)
# Example: "uploads/GSE120584_serum_norm.csv" -> "GSE120584_serum_norm"
file_name = os.path.basename(data_path).split('.')[0]

# Use custom csv_path if specified, otherwise choose a sensible default
if csv_path:
    # Use custom CSV file
    ranked_features_path = csv_path
else:
    # Prefer the canonical per-class-pair location when class_pair is provided
    if class_pair:
        ranked_features_path = os.path.join("results", file_name, "feature_ranking", class_pair, "ranked_features_df.csv")
        # Fallback to legacy location if not found later during read
    else:
        # Legacy fallback (no class_pair specified)
        ranked_features_path = os.path.join("results", file_name, "ranked_features_df.csv")

# Read the CSV file (feature ranking CSVs are written with ';' separator)
def _read_ranked_csv(path):
    try:
        _df = pd.read_csv(path, sep=';')
        if _df.shape[1] <= 1:
            _df = pd.read_csv(path)
        return _df
    except Exception:
        return pd.read_csv(path)

df = None
if os.path.exists(ranked_features_path):
    df = _read_ranked_csv(ranked_features_path)
else:
    # Final fallback: try legacy path if class_pair default was missing
    legacy_path = os.path.join("results", file_name, "ranked_features_df.csv")
    df = _read_ranked_csv(legacy_path)

# Some ranked CSVs may not include this column; ignore if missing
df.drop(columns=["overall score"], inplace=True, errors="ignore")

# Calculate mean rank robustly (coerce non-numeric, tolerate missing values)
numeric_part = df.iloc[:, 1:].apply(pd.to_numeric, errors='coerce')
mean_rank = numeric_part.mean(axis=1, skipna=True)
global_max = numeric_part.max().max()
if pd.isna(global_max):
    global_max = 1e9  # fallback if all values are NaN
# Fill NaNs with a large value to push them to the bottom, then round and cast
df["Mean Rank"] = mean_rank.fillna(global_max + 1000).round().astype(int)

# Select and sort the top N (feature_count) biomarkers with the smallest (most effective) mean rank
df_top = df.nsmallest(feature_count, "Mean Rank")

# Visualization settings - adjust for larger size
column_count = df.shape[1] - 1
# Set minimum width to 12 inches and scale by number of columns
min_width = max(12, column_count * 1.5)  
# Increase height, especially for more rows
height = min(15, feature_count/3 + 5)  
plt.figure(figsize=(min_width, height))

# Custom annotation function for heatmap
# Annotates each cell with integer value and increases font size

def annotate_heatmap(data, annot, fmt=".2f", **textkw):
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            if j == data.shape[1] - 1:  # Last column (Mean Rank)
                text = format(int(data[i, j]), "d")  # Format as integer
            else:
                text = format(int(data[i, j]), "d")
            # Increase font size for cell text
            annot[i * data.shape[1] + j].set_text(text)
            annot[i * data.shape[1] + j].set_fontsize(20)  # Increased cell font size

# Find the appropriate feature column name (feature type)
feature_column = df_top.columns[0]  # First column is feature type (microRNA, gene, etc)

# Use a more readable and high-contrast color palette ("magma")
ax = sns.heatmap(
    df_top.set_index(feature_column),  # Do not include last column
    annot=True,  # Annotate cells with numbers
    cmap="magma_r",  # Reversed magma colormap for dark background, light text
    fmt="",  # Custom format
    linewidths=0.7,  # Add more visible lines between cells
    linecolor="gray",  # Gray lines between cells
    square=False,  # Use rectangular cells
    annot_kws={"size": 14}  # Increase annotation font size
)

# Output directory (labeled per aggregation if provided)
if class_pair:
    outdir = os.path.join("results", file_name, "summaryStatisticalMethods", class_pair)
else:
    outdir = os.path.join("results", file_name, "summaryStatisticalMethods")

if agg_label:
    safe_label = re.sub(r'[^A-Za-z0-9._=+\-]+', '_', agg_label)
    outdir = os.path.join(outdir, safe_label)

# Create folders if they do not exist
os.makedirs(os.path.join(outdir, "png"), exist_ok=True)
os.makedirs(os.path.join(outdir, "pdf"), exist_ok=True)

# Apply custom annotation to heatmap
annotate_heatmap(ax.collections[0].get_array(), ax.texts)

# Adjust title font size based on length
# Use a more generic heading and include aggregation label for clarity
if class_pair:
    # Replace underscores with ' vs ' for display purposes
    class_pair_display = class_pair.replace('_', ' vs ')
    human_label = _humanize_agg_label(agg_label)
    agg_suffix = f" (Aggregation: {human_label})" if human_label else ""
    title_text = (
        f"Top {feature_count} Biomarkers and Their Rankings by Statistical Methods\n"
        f"for Class Pair: {class_pair_display}{agg_suffix}"
    )
else:
    human_label = _humanize_agg_label(agg_label)
    agg_suffix = f" (Aggregation: {human_label})" if human_label else ""
    title_text = f"Top {feature_count} Biomarkers and Their Rankings by Statistical Methods{agg_suffix}"

# Set font size
fontsize = 20 if column_count >= 5 else 18

# Set title and labels with larger font size
plt.title(title_text, fontsize=fontsize, fontweight="bold", pad=20)
plt.xticks(rotation=45, ha="right", fontsize=18)
plt.yticks(rotation=0, fontsize=18)
plt.xlabel("Statistical Methods", fontsize=24)
plt.ylabel(feature_column, fontsize=24)

# Expand and adjust plot area
plt.subplots_adjust(top=0.92, bottom=0.15, left=0.20, right=0.95)

# Apply tight_layout for proper content placement
plt.tight_layout()

# Save files with higher resolution
png_output_path = os.path.join(outdir, "png", "summary_of_statistical_methods_plot.png")
plt.savefig(png_output_path, dpi=400, bbox_inches='tight')

# Print relative path (to be used by server.js)
print(png_output_path)

# Save as PDF
pdf_output_path = os.path.join(outdir, "pdf", "summary_of_statistical_methods_plot.pdf")
plt.savefig(pdf_output_path, dpi=400, bbox_inches='tight')
