import json
import glob
import os

print("\n" + "=" * 70)
print("          TERRAFORM SECURITY SCANNER RESULTS")
print("=" * 70)

# ============================================================
# KICS
# ============================================================

print("\n\n#################### KICS ####################")

for path in sorted(glob.glob("results/kics/*/*.json")):

    case = os.path.basename(os.path.dirname(path))

    try:
        with open(path) as f:
            data = json.load(f)

        print(f"\n[{case}]")

        # KICS stores the number of findings globally.
        total = data.get("total_counter", 0)

        if total == 0:
            print("  ✓ No findings")
            continue

        print(f"  Total findings: {total}")

        severity = data.get("severity_counters", {})

        print(
            f"  Severity: "
            f"CRITICAL={severity.get('CRITICAL', 0)}, "
            f"HIGH={severity.get('HIGH', 0)}, "
            f"MEDIUM={severity.get('MEDIUM', 0)}, "
            f"LOW={severity.get('LOW', 0)}, "
            f"INFO={severity.get('INFO', 0)}"
        )

        for q in data.get("queries", []):
            print(
                f"  - {q.get('query_name', 'Unknown')} "
                f"[{q.get('severity', 'Unknown')}]"
            )

    except Exception as e:
        print(f"  ERROR: {e}")


# ============================================================
# TRIVY
# ============================================================

print("\n\n#################### TRIVY ####################")

for path in sorted(glob.glob("results/trivy/*/*.json")):

    case = os.path.basename(os.path.dirname(path))

    try:
        with open(path) as f:
            data = json.load(f)

        print(f"\n[{case}]")

        findings = []

        for result in data.get("Results", []):
            findings.extend(
                result.get("Misconfigurations", [])
            )

        if not findings:
            print("  ✓ No misconfigurations")
            continue

        print(f"  Total findings: {len(findings)}")

        for item in findings:
            print(
                f"  - {item.get('Title', 'Unknown')} "
                f"[{item.get('Severity', 'Unknown')}] "
                f"({item.get('ID', 'N/A')})"
            )

    except Exception as e:
        print(f"  ERROR: {e}")


# ============================================================
# CHECKOV
# ============================================================

print("\n\n#################### CHECKOV ####################")

for path in sorted(glob.glob("results/checkov/*/*.json")):

    case = os.path.basename(os.path.dirname(path))

    try:
        with open(path) as f:
            data = json.load(f)

        print(f"\n[{case}]")

        findings = data.get("results", {}).get(
            "failed_checks", []
        )

        if not findings:
            print("  ✓ No failed checks")
            continue

        print(f"  Total failed checks: {len(findings)}")

        for item in findings:
            print(
                f"  - {item.get('check_name', 'Unknown')} "
                f"({item.get('check_id', 'N/A')})"
            )

    except Exception as e:
        print(f"  ERROR: {e}")


print("\n" + "=" * 70)
print("                       COMPLETE")
print("=" * 70)
