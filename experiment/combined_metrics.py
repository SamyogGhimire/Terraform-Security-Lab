import csv

with open("experiment/detection_matrix.csv") as f:
    rows = list(csv.DictReader(f))

tools = ["KICS", "Trivy", "Checkov"]

TP = TN = FP = FN = 0

for row in rows:

    actual = int(row["ground_truth"])

    # Combined framework:
    # vulnerability is considered detected if ANY scanner detects it.
    predicted = max(int(row[t]) for t in tools)

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
f1 = 2 * precision * recall / (precision + recall)
accuracy = (TP + TN) / (TP + TN + FP + FN)
fpr = FP / (FP + TN) if FP + TN else 0

print("\n" + "=" * 60)
print("        MULTI-SCANNER COMBINED RESULTS")
print("=" * 60)

print(f"\nTP        : {TP}")
print(f"TN        : {TN}")
print(f"FP        : {FP}")
print(f"FN        : {FN}")
print(f"Precision : {precision*100:.2f}%")
print(f"Recall    : {recall*100:.2f}%")
print(f"F1-score  : {f1*100:.2f}%")
print(f"Accuracy  : {accuracy*100:.2f}%")
print(f"FPR       : {fpr*100:.2f}%")

print("\nCase-level combined detection:")

for row in rows:
    detected = max(int(row[t]) for t in tools)

    print(
        f"{row['case_id']:4} | "
        f"Ground truth={row['ground_truth']} | "
        f"Combined={detected}"
    )
