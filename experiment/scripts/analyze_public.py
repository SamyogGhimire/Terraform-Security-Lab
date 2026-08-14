import csv
import json
import os
from collections import defaultdict

CASES = [f"P{i:02d}" for i in range(1, 6)]
TOOLS = ["KICS", "Trivy", "Checkov"]

os.makedirs("experiment/generated/public", exist_ok=True)

def load_kics(case):
    with open(f"results/public/kics/{case}/{case}.json") as f:
        data = json.load(f)

    findings = []
    for q in data.get("queries", []):
        if q.get("files"):
            findings.append({
                "id": q.get("query_id"),
                "name": q.get("query_name"),
                "severity": q.get("severity")
            })
    return findings

def load_trivy(case):
    with open(f"results/public/trivy/{case}/{case}.json") as f:
        data = json.load(f)

    findings = []
    for result in data.get("Results", []):
        for x in result.get("Misconfigurations", []) or []:
            findings.append({
                "id": x.get("ID"),
                "name": x.get("Title"),
                "severity": x.get("Severity")
            })
    return findings

def load_checkov(case):
    path = (
        f"results/public/checkov/{case}/"
        f"results_json.json/results_json.json"
    )

    with open(path) as f:
        data = json.load(f)

    findings = []
    for x in data.get("results", {}).get("failed_checks", []):
        findings.append({
            "id": x.get("check_id"),
            "name": x.get("check_name"),
            "severity": "N/A"
        })
    return findings

loaders = {
    "KICS": load_kics,
    "Trivy": load_trivy,
    "Checkov": load_checkov
}

all_findings = defaultdict(list)

for case in CASES:
    for tool in TOOLS:
        findings = loaders[tool](case)

        for finding in findings:
            all_findings[(case, tool)].append(finding)

# ------------------------------------------------------------
# SUMMARY
# ------------------------------------------------------------

summary = []

for case in CASES:
    row = {"case_id": case}

    for tool in TOOLS:
        row[tool] = len(all_findings[(case, tool)])

    summary.append(row)

with open(
    "experiment/generated/public/public_findings.csv",
    "w",
    newline=""
) as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["case_id"] + TOOLS
    )
    writer.writeheader()
    writer.writerows(summary)

# ------------------------------------------------------------
# TOOL TOTALS
# ------------------------------------------------------------

with open(
    "experiment/generated/public/public_tool_summary.txt",
    "w"
) as f:

    f.write("PUBLIC TERRAFORM DATASET ANALYSIS\n")
    f.write("=" * 70 + "\n\n")

    for tool in TOOLS:
        total = sum(
            len(all_findings[(case, tool)])
            for case in CASES
        )

        cases = sum(
            len(all_findings[(case, tool)]) > 0
            for case in CASES
        )

        f.write(
            f"{tool:10} "
            f"Total findings={total:4} | "
            f"Cases with findings={cases}/5\n"
        )

    f.write("\nFINDINGS BY CASE\n")
    f.write("-" * 70 + "\n")

    for row in summary:
        f.write(
            f"{row['case_id']:6} "
            f"KICS={row['KICS']:3} "
            f"Trivy={row['Trivy']:3} "
            f"Checkov={row['Checkov']:3}\n"
        )

# ------------------------------------------------------------
# SEVERITY ANALYSIS
# ------------------------------------------------------------

severity = defaultdict(lambda: defaultdict(int))

for case in CASES:
    for tool in TOOLS:
        for finding in all_findings[(case, tool)]:
            sev = finding["severity"] or "UNKNOWN"
            severity[tool][sev] += 1

with open(
    "experiment/generated/public/public_severity.csv",
    "w",
    newline=""
) as f:

    writer = csv.writer(f)
    writer.writerow(["Tool", "Severity", "Findings"])

    for tool in TOOLS:
        for sev, count in sorted(severity[tool].items()):
            writer.writerow([tool, sev, count])

# ------------------------------------------------------------
# UNIQUE CHECK IDS / QUERY IDS
# ------------------------------------------------------------

with open(
    "experiment/generated/public/public_unique_findings.csv",
    "w",
    newline=""
) as f:

    writer = csv.writer(f)
    writer.writerow(["Tool", "Case", "Finding_ID", "Finding_Name"])

    for case in CASES:
        for tool in TOOLS:
            seen = set()

            for finding in all_findings[(case, tool)]:
                fid = finding["id"]

                if fid in seen:
                    continue

                seen.add(fid)

                writer.writerow([
                    tool,
                    case,
                    fid,
                    finding["name"]
                ])

print("Public analysis completed.")
print("Generated:")
print("  experiment/generated/public/public_findings.csv")
print("  experiment/generated/public/public_tool_summary.txt")
print("  experiment/generated/public/public_severity.csv")
print("  experiment/generated/public/public_unique_findings.csv")
