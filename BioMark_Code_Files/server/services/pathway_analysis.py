import json
import os
import sys
import uuid
from datetime import datetime
from typing import List

import pandas as pd
from gseapy import enrichr

DEFAULT_GENE_SET = "KEGG_2021_Human"
DEFAULT_ORGANISM = "Human"
SIGNIFICANCE_THRESHOLD = 0.05


def ensure_output_directory(base_dir: str, class_pair: str) -> str:
    results_root = os.path.abspath(base_dir) if base_dir else os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "results")
    )
    output_dir = os.path.join(results_root, "pathway_analysis")
    if class_pair:
        output_dir = os.path.join(output_dir, class_pair)
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def perform_kegg_pathway_analysis(
    analysis_results: List[str],
    results_dir: str,
    class_pair: str = "",
    organism: str = DEFAULT_ORGANISM,
):
    try:
        sanitized = [gene.strip() for gene in analysis_results if isinstance(gene, str) and gene.strip()]
        if not sanitized:
            summary = "No significant genes found in the analysis results."
            return {
                "success": False,
                "message": summary,
                "error": "No significant genes available for analysis.",
                "data": {
                    "pathwayResults": None,
                    "summary": summary,
                    "significantPathwayCount": 0,
                    "totalPathways": 0,
                    "inputGeneCount": 0,
                    "classPair": class_pair or None,
                },
            }

        enrichment = enrichr(gene_list=sanitized, gene_sets=DEFAULT_GENE_SET, organism=organism)
        results = getattr(enrichment, "results", pd.DataFrame())

        run_id = datetime.utcnow().strftime("%Y%m%d-%H%M%S") + f"_{uuid.uuid4().hex[:6]}"

        if results.empty:
            summary = "No KEGG pathways were returned for the provided genes."
            output_dir = ensure_output_directory(results_dir, class_pair)
            output_path = os.path.join(
                output_dir,
                f"kegg_pathway_analysis_results_{run_id}.csv",
            )
            results.to_csv(output_path, index=False)
            return {
                "success": True,
                "message": summary,
                "data": {
                    "pathwayResults": output_path,
                    "summary": summary,
                    "significantPathwayCount": 0,
                    "totalPathways": 0,
                    "inputGeneCount": len(sanitized),
                    "classPair": class_pair or None,
                    "runId": run_id,
                },
            }

        if "Adjusted P-value" in results.columns:
            results = results.sort_values(by="Adjusted P-value", ascending=True)
            significant_mask = results["Adjusted P-value"] < SIGNIFICANCE_THRESHOLD
            significant_pathways = results[significant_mask]
        else:
            significant_pathways = pd.DataFrame()

        output_dir = ensure_output_directory(results_dir, class_pair)
        output_path = os.path.join(
            output_dir,
            f"kegg_pathway_analysis_results_{run_id}.csv",
        )

        export_frame = significant_pathways if not significant_pathways.empty else results
        export_frame.to_csv(output_path, index=False)

        significant_count = int(significant_pathways.shape[0]) if not significant_pathways.empty else 0
        total_count = int(results.shape[0])
        summary = (
            f"KEGG pathway analysis completed: {significant_count} of {total_count} pathways "
            f"passed the significance threshold ({SIGNIFICANCE_THRESHOLD})."
        )

        return {
            "success": True,
            "message": summary,
            "data": {
                "pathwayResults": output_path,
                "summary": summary,
                "significantPathwayCount": significant_count,
                "totalPathways": total_count,
                "inputGeneCount": len(sanitized),
                "classPair": class_pair or None,
                "runId": run_id,
            },
        }
    except Exception as exc:
        summary = "KEGG pathway analysis failed due to an error."
        return {
            "success": False,
            "message": summary,
            "error": str(exc),
            "data": {
                "pathwayResults": None,
                "summary": summary,
                "significantPathwayCount": 0,
                "totalPathways": 0,
                "inputGeneCount": len(analysis_results) if analysis_results else 0,
                "classPair": class_pair or None,
                "runId": None,
            },
        }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        failure_payload = {
            "success": False,
            "message": "Pathway analysis input file was not provided.",
            "error": "Usage: python pathway_analysis.py <analysis_results.json> [results_dir] [class_pair]",
            "data": {
                "pathwayResults": None,
                "summary": "Missing input parameters prevented execution.",
                "significantPathwayCount": 0,
                "totalPathways": 0,
                "inputGeneCount": 0,
                "classPair": None,
            },
        }
        print(json.dumps(failure_payload))
        sys.exit(1)

    gene_list_path = sys.argv[1]
    provided_results_dir = sys.argv[2] if len(sys.argv) >= 3 else os.path.join(os.path.dirname(__file__), "..", "results")
    provided_class_pair = sys.argv[3] if len(sys.argv) >= 4 else ""

    try:
        with open(gene_list_path, "r", encoding="utf-8") as handle:
            raw_payload = json.load(handle)

        if isinstance(raw_payload, dict):
            candidate = raw_payload.get("analysisResults") or raw_payload.get("genes")
            analysis_results = candidate if isinstance(candidate, list) else []
        elif isinstance(raw_payload, list):
            analysis_results = raw_payload
        else:
            analysis_results = []

        result = perform_kegg_pathway_analysis(analysis_results, provided_results_dir, provided_class_pair)
        print(json.dumps(result))

        if not result.get("success", False):
            sys.exit(1)
    except Exception as exc:
        failure_payload = {
            "success": False,
            "message": "KEGG pathway analysis failed to start.",
            "error": str(exc),
            "data": {
                "pathwayResults": None,
                "summary": "Unable to load or parse the input genes.",
                "significantPathwayCount": 0,
                "totalPathways": 0,
                "inputGeneCount": 0,
                "classPair": provided_class_pair or None,
            },
        }
        print(json.dumps(failure_payload))
        sys.exit(1)