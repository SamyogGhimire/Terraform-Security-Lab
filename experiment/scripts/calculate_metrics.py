import csv

tools = ["KICS", "Trivy", "Checkov"]

with open("experiment/detection_matrix.csv") as f:
    rows = list(csv.DictReader(f))

print("\n" + "=" * 75)
print("              TERRAFORM SECURITY DETECTION METRICS")
print("=" * 75)

results = []

for tool in tools:

    TP = TN = FP = FN = 0

    for row in rows:
        actual = int(row["ground_truth"])
        predicted = int(row[tool])

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
    fnr = FN / (FN + TP) if FN + TP else 0

    results.append({
        "Tool": tool,
        "TP": TP,
        "TN": TN,
        "FP": FP,
        "FN": FN,
        "Precision": precision,
        "Recall": recall,
        "F1": f1,
        "Accuracy": accuracy,
        "FPR": fpr,
        "FNR": fnr
    })

    print(f"\n{tool}")
    print("-" * 75)
    print(f"TP        : {TP}")
    print(f"TN        : {TN}")
    print(f"FP        : {FP}")
    print(f"FN        : {FN}")
    print(f"Precision : {precision:.4f} ({precision*100:.2f}%)")
    print(f"Recall    : {recall:.4f} ({recall*100:.2f}%)")
    print(f"F1-score  : {f1:.4f} ({f1*100:.2f}%)")
    print(f"Accuracy  : {accuracy:.4f} ({accuracy*100:.2f}%)")
    print(f"FPR       : {fpr:.4f} ({fpr*100:.2f}%)")
    print(f"FNR       : {fnr:.4f} ({fnr*100:.2f}%)")


with open("experiment/metrics.csv", "w", newline="") as f:

    writer = csv.DictWriter(
        f,
        fieldnames=[
            "Tool",
            "TP",
            "TN",
            "FP",
            "FN",
            "Precision",
            "Recall",
            "F1",
            "Accuracy",
            "FPR",
            "FNR"
        ]
    )

    writer.writeheader()

    for result in results:
        writer.writerow(result)


print("\n" + "=" * 75)
print("Metrics saved to:")
print("experiment/metrics.csv")
print("=" * 75)
