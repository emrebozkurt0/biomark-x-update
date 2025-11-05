import os
import sys
import json
import re
import shutil

# Add modules path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modules.feature_selection import feature_rank
from modules.utils import load_json


def main():
    if len(sys.argv) < 3:
        print("Usage: recompute_ranking.py <filePath> <class_pair> [aggregation_method] [aggregation_weights_json] [rrf_k]", file=sys.stderr)
        sys.exit(1)

    file_path = sys.argv[1]
    class_pair = sys.argv[2]
    aggregation_method = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] else "rrf"
    aggregation_weights_json = sys.argv[4] if len(sys.argv) > 4 and sys.argv[4] else ""
    rrf_k = int(sys.argv[5]) if len(sys.argv) > 5 and sys.argv[5] else 60
    agg_label = sys.argv[6] if len(sys.argv) > 6 and sys.argv[6] else ""

    base_name = os.path.basename(file_path)
    file_name_without_ext = os.path.splitext(base_name)[0]
    outdir = os.path.join("results", file_name_without_ext)

    feature_importances_path = os.path.join(outdir, "feature_importances.json")
    if not os.path.exists(feature_importances_path):
        print(f"feature_importances.json not found at: {feature_importances_path}", file=sys.stderr)
        sys.exit(2)

    data = load_json(feature_importances_path)
    if not isinstance(data, dict) or class_pair not in data:
        print(f"Class pair '{class_pair}' not found in feature_importances.json", file=sys.stderr)
        sys.exit(3)

    try:
        weights = json.loads(aggregation_weights_json) if aggregation_weights_json else None
    except Exception:
        weights = None

    filtered = {class_pair: data[class_pair]}

    # Recompute ranking CSV using selected aggregation
    feature_rank(
        top_features=filtered,
        num_top_features=100,  # compute sufficiently large; downstream shows top-N
        feature_type="microRNA",
        outdir=outdir,
        aggregation=aggregation_method,
        aggregation_weights=weights,
        rrf_k=rrf_k
    )

    # Print path to the generated CSV for optional consumers
    csv_path = os.path.join(outdir, "feature_ranking", class_pair, "ranked_features_df.csv")
    if agg_label:
        # Create a label-specific copy to avoid overwriting previous runs
        safe_label = re.sub(r'[^A-Za-z0-9._=+\-]+', '_', agg_label)
        labeled_dir = os.path.join(outdir, "feature_ranking", class_pair, safe_label)
        os.makedirs(labeled_dir, exist_ok=True)
        labeled_csv = os.path.join(labeled_dir, "ranked_features_df.csv")
        try:
            shutil.copyfile(csv_path, labeled_csv)
            print(labeled_csv)
        except Exception:
            # Fallback to default path if copy fails
            print(csv_path)
    else:
        print(csv_path)


if __name__ == "__main__":
    main()


