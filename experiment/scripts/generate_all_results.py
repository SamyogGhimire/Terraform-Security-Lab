import json
import csv
import os
from collections import Counter

CASES = [f"S{i:02d}" for i in range(1, 11)] + [f"B{i:02d}" for i in range(1, 11)]
TOOLS = ["KICS", "Trivy", "Checkov"]

os.makedirs("experiment/generated", exist_ok=True)

def load_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception as e:
        print(f"WARNING: Could not read {path}: {e}")
        return {}

def kics_count(data):
    return data.get("total_counter", 0)

def trivy_count(data):
    results = data.get("Results", [])
    return sum(len(r.get("Misconfigurations", []) or []) for r in results)

def checkov_count(data):
    # Checkov JSON normally stores failed checks in check_type-specific results.
    count = 0

    for key in ["results", "failed_checks"]:
        value = data.get(key)

        if isinstance(value, dict):
            failed = value.get("failed_checks", [])
            if isinstance(failed, list):
                count += len(failed)

        elif isinstance(value, list):
            count += len(value)

    return count


def get_counts(case, tool):
    if tool == "KICS":
        path = f"results/kics/{case}/{case}.json"
        return kics_count(load_json(path))

    if tool == "Trivy":
        path = f"results/trivy/{case}/{case}.json"
        return trivy_count(load_json(path))

    if tool == "Checkov":
        path = f"results/checkov/{case}/results_json.json"
        return checkov_count(load_json(path))


# ------------------------------------------------------------
# FINDING COUNTS
# ------------------------------------------------------------

rows = []

for case in CASES:
    corpus = "synthetic" if case.startswith("S") else "baseline"
    ground_truth = 1 if case.startswith("S") else 0

    counts = {
        tool: get_counts(case, tool)
        for tool in TOOLS
    }

    rows.append({
        "case_id": case,
        "corpus": corpus,
        "ground_truth": ground_truth,
        **counts
    })


with open("experiment/generated/finding_counts.csv", "w", newline="") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["case_id", "corpus", "ground_truth"] + TOOLS
    )
    writer.writeheader()
    writer.writerows(rows)


# ------------------------------------------------------------
# CASE-LEVEL DETECTION
# ------------------------------------------------------------

detection_rows = []

for row in rows:
    output = {
        "case_id": row["case_id"],
        "corpus": row["corpus"],
        "ground_truth": row["ground_truth"]
    }

    for tool in TOOLS:
        output[tool] = 1 if row[tool] > 0 else 0

    detection_rows.append(output)


with open("experiment/generated/detection_matrix.csv", "w", newline="") as f:
    writer = csv.DictWriter(
        f,
        fieldnames=["case_id", "corpus", "ground_truth"] + TOOLS
    )
    writer.writeheader()
    writer.writerows(detection_rows)


# ------------------------------------------------------------
# METRICS
# ------------------------------------------------------------

def metrics(tool):
    TP = TN = FP = FN = 0

    for row in detection_rows:
        actual = row["ground_truth"]
        predicted = row[tool]

        if actual == 1 and predicted == 1:
            TP += 1
        elif actual == 0 and predicted == 0:
            TN += 1
        elif actual == 0 and predicted == 1:
            FP += 1
        elif actual == 1 and predicted == 0:
            FN += 1

    precision = TP / (TP + FP) if TP + FP else 0
    recall = TP / (TP + FN) if TP + FN else 0
    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall else 0
    )
    accuracy = (TP + TN) / (TP + TN + FP + FN)
    fpr = FP / (FP + TN) if FP + TN else 0

    return TP, TN, FP, FN, precision, recall, f1, accuracy, fpr


with open("experiment/generated/tool_metrics.csv", "w", newline="") as f:

    writer = csv.writer(f)

    writer.writerow([
        "Tool",
        "TP",
        "TN",
        "FP",
        "FN",
        "Precision",
        "Recall",
        "F1",
        "Accuracy",
        "FPR"
    ])

    for tool in TOOLS:
        values = metrics(tool)

        writer.writerow([
            tool,
            *values[:4],
            *[round(x * 100, 2) for x in values[4:]]
        ])


# ------------------------------------------------------------
# COMBINED FRAMEWORK
# ------------------------------------------------------------

TP = TN = FP = FN = 0

for row in detection_rows:

    actual = row["ground_truth"]

    # Any scanner detecting = combined framework detection
    predicted = max(row[t] for t in TOOLS)

    if actual == 1 and predicted == 1:
        TP += 1
    elif actual == 0 and predicted == 0:
        TN += 1
    elif actual == 0 and predicted == 1:
        FP += 1
    elif actual == 1 and predicted == 0:
        FN += 1

precision = TP / (TP + FP) if TP + FP else 0
recall = TP / (TP + FN) if TP + FN else 0
f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0
accuracy = (TP + TN) / (TP + TN + FP + FN)
fpr = FP / (FP + TN) if FP + TN else 0

with open("experiment/generated/combined_metrics.txt", "w") as f:
    f.write("COMBINED SECURITY VALIDATION FRAMEWORK\n")
    f.write("=" * 50 + "\n\n")
    f.write(f"TP        : {TP}\n")
    f.write(f"TN        : {TN}\n")
    f.write(f"FP        : {FP}\n")
    f.write(f"FN        : {FN}\n")
    f.write(f"Precision : {precision*100:.2f}%\n")
    f.write(f"Recall    : {recall*100:.2f}%\n")
    f.write(f"F1-score  : {f1*100:.2f}%\n")
    f.write(f"Accuracy  : {accuracy*100:.2f}%\n")
    f.write(f"FPR       : {fpr*100:.2f}%\n")


# ------------------------------------------------------------
# HUMAN-READABLE SUMMARY
# ------------------------------------------------------------

with open("experiment/generated/experiment_summary.txt", "w") as f:

    f.write("=" * 70 + "\n")
    f.write("TERRAFORM SECURITY VALIDATION EXPERIMENT\n")
    f.write("=" * 70 + "\n\n")

    f.write("DATASET\n")
    f.write("-" * 70 + "\n")
    f.write("Synthetic vulnerable cases : 10\n")
    f.write("Secure baseline cases      : 10\n")
    f.write("Total cases                : 20\n")
    f.write("Security scanners          : KICS, Trivy, Checkov\n\n")

    f.write("FINDINGS BY TOOL\n")
    f.write("-" * 70 + "\n")

    for tool in TOOLS:

        vulnerable = sum(
            r[tool] for r in rows if r["ground_truth"] == 1
        )

        baseline = sum(
            r[tool] for r in rows if r["ground_truth"] == 0
        )

        f.write(
            f"{tool:10} Vulnerable={vulnerable:4} "
            f"Baseline={baseline:4} "
            f"Total={vulnerable + baseline:4}\n"
        )

    f.write("\nCASE-LEVEL FINDINGS\n")
    f.write("-" * 70 + "\n")

    f.write(
        f"{'Case':<8}"
        f"{'KICS':>8}"
        f"{'Trivy':>8}"
        f"{'Checkov':>10}\n"
    )

    for r in rows:
        f.write(
            f"{r['case_id']:<8}"
            f"{r['KICS']:>8}"
            f"{r['Trivy']:>8}"
            f"{r['Checkov']:>10}\n"
        )

    f.write("\nTOOL METRICS\n")
    f.write("-" * 70 + "\n")

    for tool in TOOLS:

        TP, TN, FP, FN, p, r, f1, acc, fpr = metrics(tool)

        f.write(f"\n{tool}\n")
        f.write(f"TP        : {TP}\n")
        f.write(f"TN        : {TN}\n")
        f.write(f"FP        : {FP}\n")
        f.write(f"FN        : {FN}\n")
        f.write(f"Precision : {p*100:.2f}%\n")
        f.write(f"Recall    : {r*100:.2f}%\n")
        f.write(f"F1-score  : {f1*100:.2f}%\n")
        f.write(f"Accuracy  : {acc*100:.2f}%\n")
        f.write(f"FPR       : {fpr*100:.2f}%\n")

print()
print("=" * 70)
print("EXPERIMENT ANALYSIS COMPLETE")
print("=" * 70)
print()
print("Generated:")
print("  experiment/generated/finding_counts.csv")
print("  experiment/generated/detection_matrix.csv")
print("  experiment/generated/tool_metrics.csv")
print("  experiment/generated/combined_metrics.txt")
print("  experiment/generated/experiment_summary.txt")
print()
