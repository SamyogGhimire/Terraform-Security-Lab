import csv
from pathlib import Path

matrix = Path("experiment/results/detection_matrix.csv")
out = Path("experiment/results")
out.mkdir(parents=True, exist_ok=True)

with matrix.open() as f:
    rows = list(csv.DictReader(f))

tools = ["KICS", "Trivy", "Checkov"]

def calc(preds):
    TP = TN = FP = FN = 0

    for actual, predicted in preds:
        if actual == 1 and predicted == 1:
            TP += 1
        elif actual == 0 and predicted == 0:
            TN += 1
        elif actual == 0 and predicted == 1:
            FP += 1
        else:
            FN += 1

    precision = TP / (TP + FP) if TP + FP else 0
    recall = TP / (TP + FN) if TP + FN else 0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0
    accuracy = (TP + TN) / (TP + TN + FP + FN)
    fpr = FP / (FP + TN) if FP + TN else 0

    return TP, TN, FP, FN, precision, recall, f1, accuracy, fpr

results = []

for tool in tools:
    preds = [(int(r["ground_truth"]), int(r[tool])) for r in rows]
    vals = calc(preds)
    results.append((tool, *vals))

combined_preds = []
for r in rows:
    combined = max(int(r[t]) for t in tools)
    combined_preds.append((int(r["ground_truth"]), combined))

combined = calc(combined_preds)
results.append(("Combined", *combined))

with open(out / "tool_metrics.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Tool","TP","TN","FP","FN","Precision","Recall","F1","Accuracy","FPR"])
    for row in results:
        writer.writerow([
            row[0], *row[1:5],
            *[round(v * 100, 2) for v in row[5:]]
        ])

with open(out / "metrics.txt", "w") as f:
    for row in results:
        f.write("=" * 50 + "\n")
        f.write(row[0] + "\n")
        f.write("=" * 50 + "\n")
        f.write(f"TP        : {row[1]}\n")
        f.write(f"TN        : {row[2]}\n")
        f.write(f"FP        : {row[3]}\n")
        f.write(f"FN        : {row[4]}\n")
        f.write(f"Precision : {row[5]*100:.2f}%\n")
        f.write(f"Recall    : {row[6]*100:.2f}%\n")
        f.write(f"F1-score  : {row[7]*100:.2f}%\n")
        f.write(f"Accuracy  : {row[8]*100:.2f}%\n")
        f.write(f"FPR       : {row[9]*100:.2f}%\n\n")

print("Generated:")
print("  experiment/results/tool_metrics.csv")
print("  experiment/results/metrics.txt")
