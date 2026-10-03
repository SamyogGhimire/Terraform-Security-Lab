#!/usr/bin/env python3
"""
Resource-level agreement between KICS, Trivy and Checkov on the 25-repo
independent benchmark.

The three scanners use entirely different rule-ID namespaces (KICS GUIDs,
Trivy AVD-IDs, Checkov CKV_* IDs), so there is no way to match "the same
finding" across tools by rule ID. What *can* be compared is which Terraform
resource each tool flagged at least one finding on, normalized to
`<resource_type>.<resource_label>` (dropping any enclosing module-path
prefix, since each tool renders that prefix differently).

This gives a resource-level Jaccard overlap: how much do the tools'
*attention* agree, independent of which specific rule fired. It is
deliberately coarser than finding-level overlap and is reported as such -
see the caveat printed at the end of this script's output.
"""

import json
from collections import defaultdict
from pathlib import Path

BASE = Path("results/independent/iacsecbench")
OUTPUT = Path("experiment/generated/independent")
TOOLS = ["KICS", "Trivy", "Checkov"]


def load_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def normalize(addr):
    """Reduce a resource address to its last two dot-separated segments."""
    parts = [p for p in addr.split(".") if p]
    if len(parts) >= 2:
        return ".".join(parts[-2:])
    return addr


def kics_resources(repo_id):
    path = BASE / "kics" / repo_id / "results.json"
    data = load_json(path)
    if not data:
        return set()

    resources = set()
    for query in data.get("queries", []):
        for f in query.get("files", []):
            search_key = f.get("search_key", "")
            if "[" in search_key and search_key.endswith("]"):
                rtype, label = search_key.split("[", 1)
                resources.add(normalize(f"{rtype}.{label[:-1]}"))
            else:
                rtype = f.get("resource_type")
                name = f.get("resource_name")
                if rtype and name:
                    resources.add(normalize(f"{rtype}.{name}"))
    return resources


def trivy_resources(repo_id):
    path = BASE / "trivy" / repo_id / "results.json"
    data = load_json(path)
    if not data:
        return set()

    resources = set()
    for result in data.get("Results", []):
        for mc in result.get("Misconfigurations", []) or []:
            cause = mc.get("CauseMetadata", {}) or {}
            addr = cause.get("Resource")
            if addr:
                resources.add(normalize(addr))
    return resources


def find_checkov_json(repo_id):
    directory = BASE / "checkov" / repo_id / "results.json"
    if not directory.exists():
        return None
    if directory.is_file():
        return directory
    files = list(directory.rglob("*.json"))
    return files[0] if files else None


def checkov_resources(repo_id):
    path = find_checkov_json(repo_id)
    if path is None:
        return set()

    data = load_json(path)
    if data is None:
        return set()

    reports = data if isinstance(data, list) else [data]
    resources = set()

    for report in reports:
        if not isinstance(report, dict):
            continue
        failed = report.get("results", {}).get("failed_checks", [])
        if not isinstance(failed, list):
            continue
        for finding in failed:
            if not isinstance(finding, dict):
                continue
            addr = finding.get("resource")
            if addr:
                resources.add(normalize(addr))
    return resources


def jaccard(a, b):
    if not a and not b:
        return None
    union = a | b
    if not union:
        return None
    return len(a & b) / len(union)


def main():
    repositories = sorted(
        p.name for p in (BASE / "kics").iterdir() if p.is_dir()
    )

    per_repo_rows = []
    agreement_counts = defaultdict(int)  # number of tools flagging each (repo, resource)

    for repo_id in repositories:
        res = {
            "KICS": kics_resources(repo_id),
            "Trivy": trivy_resources(repo_id),
            "Checkov": checkov_resources(repo_id),
        }

        all_resources = res["KICS"] | res["Trivy"] | res["Checkov"]
        for r in all_resources:
            n_tools = sum(1 for t in TOOLS if r in res[t])
            agreement_counts[n_tools] += 1

        row = {"repository": repo_id}
        for a, b in [("KICS", "Trivy"), ("KICS", "Checkov"), ("Trivy", "Checkov")]:
            j = jaccard(res[a], res[b])
            row[f"jaccard_{a}_{b}"] = round(j, 4) if j is not None else ""
        row["flagged_resources_union"] = len(all_resources)
        per_repo_rows.append(row)

    import csv

    out_csv = OUTPUT / "resource_overlap.csv"
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(per_repo_rows[0].keys()))
        writer.writeheader()
        writer.writerows(per_repo_rows)

    total_resources = sum(agreement_counts.values())
    summary_lines = [
        "RESOURCE-LEVEL SCANNER AGREEMENT (25-repo independent benchmark)",
        "=" * 70,
        "",
        "A 'resource' here is <resource_type>.<label>, collapsed across any",
        "enclosing module path. A tool 'flags' a resource if it produced at",
        "least one finding on it, regardless of which specific rule fired.",
        "This is coarser than rule-level matching, which isn't possible",
        "across tools with incompatible rule-ID namespaces.",
        "",
        f"Distinct flagged resources across all repos: {total_resources}",
        "",
    ]
    for n in [1, 2, 3]:
        count = agreement_counts.get(n, 0)
        pct = count / total_resources * 100 if total_resources else 0
        summary_lines.append(
            f"Flagged by exactly {n} tool(s): {count:5} ({pct:5.2f}%)"
        )

    summary_lines.append("")
    summary_lines.append("Mean pairwise Jaccard index across repositories:")
    for a, b in [("KICS", "Trivy"), ("KICS", "Checkov"), ("Trivy", "Checkov")]:
        vals = [
            row[f"jaccard_{a}_{b}"]
            for row in per_repo_rows
            if row[f"jaccard_{a}_{b}"] != ""
        ]
        mean_j = sum(vals) / len(vals) if vals else 0
        summary_lines.append(
            f"  {a} vs {b}: {mean_j:.4f}  (n={len(vals)} repos with overlap data)"
        )

    summary_lines.append("")
    summary_lines.append(
        "Interpretation: a low Jaccard index and a high share of resources "
        "flagged by only one tool both support the complementarity claim - "
        "the scanners are largely looking at different parts of each "
        "repository's resource graph, not re-flagging the same resources "
        "with different rule IDs."
    )

    out_txt = OUTPUT / "resource_overlap_summary.txt"
    out_txt.write_text("\n".join(summary_lines) + "\n")

    print("\n".join(summary_lines))
    print()
    print(f"Written: {out_csv}")
    print(f"Written: {out_txt}")


if __name__ == "__main__":
    main()
