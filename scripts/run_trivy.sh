#!/bin/bash

set -e

mkdir -p results/trivy

echo ""
echo "============================================================"
echo "              TERRAFORM TRIVY SECURITY SCAN"
echo "============================================================"
echo ""

TOTAL=0
PASSED=0
FINDINGS=0

for dir in dataset/synthetic/* dataset/secure/*; do

    case_id=$(basename "$dir")
    TOTAL=$((TOTAL + 1))

    echo "------------------------------------------------------------"
    echo "Scanning case: $case_id"
    echo "Location: $dir"
    echo "------------------------------------------------------------"

    mkdir -p "results/trivy/$case_id"

    trivy config "$dir" \
        --format json \
        --output "results/trivy/$case_id/$case_id.json" \
        >/dev/null 2>&1

    if [ $? -eq 0 ]; then
        echo "Status: Scan completed"
    else
        echo "Status: Scan completed with findings/errors"
    fi

    # Count detected vulnerabilities
    COUNT=$(python3 - "$case_id" <<'PY'
import json
import sys

case_id = sys.argv[1]
path = f"results/trivy/{case_id}/{case_id}.json"

try:
    with open(path) as f:
        data = json.load(f)

    count = 0

    for result in data.get("Results", []):
        count += len(result.get("Misconfigurations", []))

    print(count)

except Exception:
    print(0)
PY
)

    if [ "$COUNT" -gt 0 ]; then
        echo "Findings detected: $COUNT"
        FINDINGS=$((FINDINGS + COUNT))
    else
        echo "Findings detected: 0"
        PASSED=$((PASSED + 1))
    fi

    echo ""

done

echo "============================================================"
echo "                  TRIVY SCAN SUMMARY"
echo "============================================================"
echo "Cases scanned       : $TOTAL"
echo "Cases with findings : $((TOTAL - PASSED))"
echo "Cases with no findings: $PASSED"
echo "Total findings      : $FINDINGS"
echo "============================================================"
echo ""
echo "Detailed JSON results:"
echo "results/trivy/<CASE>/<CASE>.json"
echo ""