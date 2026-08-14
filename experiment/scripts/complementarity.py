import csv

with open("experiment/detection_matrix.csv") as f:
    rows = list(csv.DictReader(f))

tools = ["KICS", "Trivy", "Checkov"]

print("=" * 65)
print("VULNERABLE CASE DETECTION")
print("=" * 65)

vulnerable = [r for r in rows if r["ground_truth"] == "1"]

for row in vulnerable:
    detected = [t for t in tools if row[t] == "1"]
    missed = [t for t in tools if row[t] == "0"]

    print(f"\n{row['case_id']} - {row['target_vulnerability']}")
    print(f"  Detected by : {', '.join(detected)}")
    print(f"  Missed by   : {', '.join(missed) if missed else 'None'}")

print("\n" + "=" * 65)
print("PAIRWISE OVERLAP")
print("=" * 65)

for i in range(len(tools)):
    for j in range(i + 1, len(tools)):
        a = tools[i]
        b = tools[j]

        both = sum(1 for r in vulnerable if r[a] == "1" and r[b] == "1")
        a_only = sum(1 for r in vulnerable if r[a] == "1" and r[b] == "0")
        b_only = sum(1 for r in vulnerable if r[a] == "0" and r[b] == "1")

        print(f"\n{a} vs {b}")
        print(f"  Both detected : {both}")
        print(f"  {a} only      : {a_only}")
        print(f"  {b} only      : {b_only}")

print("\n" + "=" * 65)
print("COMBINED COVERAGE")
print("=" * 65)

combined = 0

for row in vulnerable:
    if any(row[t] == "1" for t in tools):
        combined += 1

print(f"Vulnerable cases : {len(vulnerable)}")
print(f"Detected         : {combined}")
print(f"Missed           : {len(vulnerable) - combined}")
print(f"Coverage         : {combined / len(vulnerable) * 100:.2f}%")
