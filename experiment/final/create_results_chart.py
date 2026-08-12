import matplotlib.pyplot as plt

tools = ["KICS", "Trivy", "Checkov", "Combined"]
precision = [100, 100, 100, 100]
recall = [80, 60, 80, 100]
f1 = [88.89, 75, 88.89, 100]
accuracy = [90, 80, 90, 100]

x = range(len(tools))

plt.figure(figsize=(10, 6))

plt.plot(x, precision, marker="o", label="Precision")
plt.plot(x, recall, marker="o", label="Recall")
plt.plot(x, f1, marker="o", label="F1-score")
plt.plot(x, accuracy, marker="o", label="Accuracy")

plt.xticks(x, tools)
plt.ylabel("Percentage (%)")
plt.ylim(0, 110)
plt.title("Security Scanner Performance Comparison")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()

plt.savefig(
    "experiment/final/scanner_performance.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

print("Chart saved to experiment/final/scanner_performance.png")
