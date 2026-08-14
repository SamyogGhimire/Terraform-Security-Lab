import csv
import matplotlib.pyplot as plt

INPUT = "experiment/generated/tool_metrics.csv"
OUTPUT = "experiment/generated"

with open(INPUT, newline="") as f:
    rows = list(csv.DictReader(f))

tools = [row["Tool"] for row in rows]
precision = [float(row["Precision"]) for row in rows]
recall = [float(row["Recall"]) for row in rows]
f1 = [float(row["F1"]) for row in rows]
accuracy = [float(row["Accuracy"]) for row in rows]

x = range(len(tools))
width = 0.2

# --------------------------------------------------
# 1. Overall Scanner Performance
# --------------------------------------------------

plt.figure(figsize=(10, 6))

plt.bar([i - 1.5 * width for i in x], precision, width, label="Precision")
plt.bar([i - 0.5 * width for i in x], recall, width, label="Recall")
plt.bar([i + 0.5 * width for i in x], f1, width, label="F1-score")
plt.bar([i + 1.5 * width for i in x], accuracy, width, label="Accuracy")

plt.xticks(list(x), tools)
plt.ylabel("Percentage")
plt.xlabel("Security Scanner")
plt.title("Security Scanner Performance")
plt.ylim(0, 110)
plt.legend()
plt.tight_layout()

plt.savefig(f"{OUTPUT}/scanner_performance.png", dpi=300)
plt.close()

# --------------------------------------------------
# 2. Recall
# --------------------------------------------------

plt.figure(figsize=(8, 5))

plt.bar(tools, recall)

plt.ylabel("Recall (%)")
plt.xlabel("Security Scanner")
plt.title("Vulnerability Detection Recall")
plt.ylim(0, 110)
plt.tight_layout()

plt.savefig(f"{OUTPUT}/recall_comparison.png", dpi=300)
plt.close()

# --------------------------------------------------
# 3. F1-score
# --------------------------------------------------

plt.figure(figsize=(8, 5))

plt.bar(tools, f1)

plt.ylabel("F1-score (%)")
plt.xlabel("Security Scanner")
plt.title("Security Scanner F1-score")
plt.ylim(0, 110)
plt.tight_layout()

plt.savefig(f"{OUTPUT}/f1_comparison.png", dpi=300)
plt.close()

# --------------------------------------------------
# 4. False Positive Rate
# --------------------------------------------------

fpr = [float(row["FPR"]) for row in rows]

plt.figure(figsize=(8, 5))

plt.bar(tools, fpr)

plt.ylabel("False Positive Rate (%)")
plt.xlabel("Security Scanner")
plt.title("False Positive Rate Comparison")
plt.ylim(0, 110)
plt.tight_layout()

plt.savefig(f"{OUTPUT}/fpr_comparison.png", dpi=300)
plt.close()

print("==============================================")
print("GRAPH GENERATION COMPLETE")
print("==============================================")
print(f"Generated: {OUTPUT}/scanner_performance.png")
print(f"Generated: {OUTPUT}/recall_comparison.png")
print(f"Generated: {OUTPUT}/f1_comparison.png")
print(f"Generated: {OUTPUT}/fpr_comparison.png")
