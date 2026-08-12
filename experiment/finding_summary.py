import re

# Manually derived from the scanner outputs already collected.
data = {
    "KICS": {
        "B01": 4, "B02": 7, "B03": 2, "B04": 8, "B05": 4,
        "S01": 10, "S02": 9, "S03": 5, "S04": 10, "S05": 4
    },
    "Trivy": {
        "B01": 4, "B02": 4, "B03": 0, "B04": 5, "B05": 8,
        "S01": 8, "S02": 5, "S03": 0, "S04": 5, "S05": 9
    },
    "Checkov": {
        "B01": 6, "B02": 3, "B03": 0, "B04": 8, "B05": 7,
        "S01": 12, "S02": 4, "S03": 9, "S04": 8, "S05": 7
    }
}

print("=" * 60)
print("FINDING-LEVEL SUMMARY")
print("=" * 60)

for tool, cases in data.items():
    baseline = sum(cases[c] for c in ["B01", "B02", "B03", "B04", "B05"])
    synthetic = sum(cases[c] for c in ["S01", "S02", "S03", "S04", "S05"])

    print(f"\n{tool}")
    print(f"  Vulnerable cases findings : {synthetic}")
    print(f"  Baseline findings         : {baseline}")
    print(f"  Total findings            : {synthetic + baseline}")

print("\n" + "=" * 60)
print("CASE-LEVEL FINDING COUNTS")
print("=" * 60)

print(f"{'Case':<8}{'KICS':>10}{'Trivy':>10}{'Checkov':>10}")

for case in ["S01","S02","S03","S04","S05","B01","B02","B03","B04","B05"]:
    print(
        f"{case:<8}"
        f"{data['KICS'][case]:>10}"
        f"{data['Trivy'][case]:>10}"
        f"{data['Checkov'][case]:>10}"
    )
