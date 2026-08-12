import csv

with open("experiment/detection_matrix.csv") as f:
    rows = list(csv.DictReader(f))

tools = ["KICS", "Trivy", "Checkov"]

print("=" * 70)
print("FINAL TOOL COMPARISON")
print("=" * 70)

for tool in tools:
    tp = tn = fp = fn = 0

    for row in rows:
        actual = int(row["ground_truth"])
        predicted = int(row[tool])

        if actual == 1 and predicted == 1:
            tp += 1
        elif actual == 0 and predicted == 0:
            tn += 1
        elif actual == 0 and predicted == 1:
            fp += 1
        elif actual == 1 and predicted == 0:
            fn += 1

    precision = tp / (tp + fp) if tp + fp else 0
    recall = tp / (tp + fn) if tp + fn else 0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0
    accuracy = (tp + tn) / (tp + tn + fp + fn)
    fpr = fp / (fp + tn) if fp + tn else 0

    print(f"\n{tool}")
    print("-" * 30)
    print(f"TP        : {tp}")
    print(f"TN        : {tn}")
    print(f"FP        : {fp}")
    print(f"FN        : {fn}")
    print(f"Precision : {precision:.2%}")
    print(f"Recall    : {recall:.2%}")
    print(f"F1-score  : {f1:.2%}")
    print(f"Accuracy  : {accuracy:.2%}")
    print(f"FPR       : {fpr:.2%}")

print("\n" + "=" * 70)
print("COMBINED FRAMEWORK")
print("=" * 70)

tp = tn = fp = fn = 0

for row in rows:
    actual = int(row["ground_truth"])
    predicted = max(int(row[t]) for t in tools)

    if actual == 1 and predicted == 1:
        tp += 1
    elif actual == 0 and predicted == 0:
        tn += 1
    elif actual == 0 and predicted == 1:
        fp += 1
    elif actual == 1 and predicted == 0:
        fn += 1

precision = tp / (tp + fp) if tp + fp else 0
recall = tp / (tp + fn) if tp + fn else 0
f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0
accuracy = (tp + tn) / (tp + tn + fp + fn)
fpr = fp / (fp + tn) if fp + tn else 0

print(f"TP        : {tp}")
print(f"TN        : {tn}")
print(f"FP        : {fp}")
print(f"FN        : {fn}")
print(f"Precision : {precision:.2%}")
print(f"Recall    : {recall:.2%}")
print(f"F1-score  : {f1:.2%}")
print(f"Accuracy  : {accuracy:.2%}")
print(f"FPR       : {fpr:.2%}")
