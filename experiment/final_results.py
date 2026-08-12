import csv

with open("experiment/detection_matrix.csv") as f:
    rows = list(csv.DictReader(f))

tools = ["KICS", "Trivy", "Checkov"]

results = []

for tool in tools:
    TP = TN = FP = FN = 0

    for r in rows:
        actual = int(r["ground_truth"])
        predicted = int(r[tool])

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
    accuracy = (TP + TN) / len(rows)
    fpr = FP / (FP + TN) if FP + TN else 0
    fnr = FN / (FN + TP) if FN + TP else 0

    results.append([
        tool, TP, TN, FP, FN,
        precision * 100,
        recall * 100,
        f1 * 100,
        accuracy * 100,
        fpr * 100,
        fnr * 100
    ])

# Combined
TP = TN = FP = FN = 0

for r in rows:
    actual = int(r["ground_truth"])
    predicted = max(int(r[t]) for t in tools)

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
accuracy = (TP + TN) / len(rows)
fpr = FP / (FP + TN) if FP + TN else 0
fnr = FN / (FN + TP) if FN + TP else 0

results.append([
    "Combined",
    TP, TN, FP, FN,
    precision * 100,
    recall * 100,
    f1 * 100,
    accuracy * 100,
    fpr * 100,
    fnr * 100
])

headers = [
    "Tool", "TP", "TN", "FP", "FN",
    "Precision", "Recall", "F1",
    "Accuracy", "FPR", "FNR"
]

with open("experiment/final_results.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(headers)
    writer.writerows(results)

print("\n" + "=" * 90)
print("FINAL EXPERIMENTAL RESULTS")
print("=" * 90)

print(
    f"{'Tool':<12}"
    f"{'TP':>5}"
    f"{'TN':>5}"
    f"{'FP':>5}"
    f"{'FN':>5}"
    f"{'Precision':>12}"
    f"{'Recall':>10}"
    f"{'F1':>10}"
    f"{'Accuracy':>12}"
)

print("-" * 90)

for r in results:
    print(
        f"{r[0]:<12}"
        f"{r[1]:>5}"
        f"{r[2]:>5}"
        f"{r[3]:>5}"
        f"{r[4]:>5}"
        f"{r[5]:>11.2f}%"
        f"{r[6]:>9.2f}%"
        f"{r[7]:>9.2f}%"
        f"{r[8]:>11.2f}%"
    )

print("=" * 90)

print("\nSaved:")
print("experiment/final_results.csv")
