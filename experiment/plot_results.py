import csv
import matplotlib.pyplot as plt

tools = []
precision = []
recall = []
f1 = []

with open("experiment/final_results.csv") as f:
    for row in csv.DictReader(f):
        tools.append(row["Tool"])
        precision.append(float(row["Precision"]))
        recall.append(float(row["Recall"]))
        f1.append(float(row["F1"]))

x = range(len(tools))
width = 0.25

plt.figure(figsize=(10, 6))

plt.bar(
    [i - width for i in x],
    precision,
    width,
    label="Precision"
)

plt.bar(
    x,
    recall,
    width,
    label="Recall"
)

plt.bar(
    [i + width for i in x],
    f1,
    width,
    label="F1-score"
)

plt.xticks(list(x), tools)
plt.ylabel("Score (%)")
plt.xlabel("Security Scanner")
plt.title("Security Scanner Performance Comparison")
plt.ylim(0, 110)
plt.legend()
plt.tight_layout()

plt.savefig(
    "experiment/scanner_performance.png",
    dpi=300
)

print("Saved: experiment/scanner_performance.png")
