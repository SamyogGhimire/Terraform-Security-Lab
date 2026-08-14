import csv
from pathlib import Path
import matplotlib.pyplot as plt

Path("experiment/graphs").mkdir(exist_ok=True)

with open("experiment/results/tool_metrics.csv") as f:
    rows = list(csv.DictReader(f))

tools = [r["Tool"] for r in rows]

metrics = ["Precision", "Recall", "F1", "Accuracy", "FPR"]

for metric in metrics:
    values = [float(r[metric]) for r in rows]

    plt.figure(figsize=(8,5))
    plt.bar(tools, values)
    plt.ylim(0, 105)
    plt.ylabel(metric + " (%)")
    plt.title(metric + " Comparison")
    plt.tight_layout()
    plt.savefig(f"experiment/graphs/{metric.lower()}_final.png")
    plt.close()

print("Final graphs generated in experiment/graphs/")
