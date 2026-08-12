#!/bin/bash

set -e

mkdir -p results/checkov

echo ""
echo "============================================================"
echo "             CHECKOV TERRAFORM SECURITY SCAN"
echo "============================================================"
echo ""

TOTAL=0
CASES_WITH_FINDINGS=0
TOTAL_FAILED_CHECKS=0

for dir in dataset/synthetic/* dataset/secure/*; do

    case_id=$(basename "$dir")
    TOTAL=$((TOTAL + 1))

    echo "------------------------------------------------------------"
    echo "CASE: $case_id"
    echo "TARGET: $dir"
    echo "------------------------------------------------------------"

    mkdir -p "results/checkov/$case_id"

    checkov \
        -d "$dir" \
        --output json \
        --output-file-path "results/checkov/$case_id" \
        >/dev/null 2>&1 || true

    JSON=$(find "results/checkov/$case_id" -type f -name "*.json" | head -1)

    if [ -n "$JSON" ] && [ -f "$JSON" ]; then

        COUNT=$(python3 - "$JSON" <<'PY'
import json
import sys

with open(sys.argv[1]) as f:
    data = json.load(f)

count = 0

if isinstance(data, dict):
    count = data.get("summary", {}).get("failed", 0)

print(count)
PY
)

        if [ "$COUNT" -gt 0 ]; then
            echo "RESULT : Failed checks detected"
            echo "COUNT  : $COUNT"
            CASES_WITH_FINDINGS=$((CASES_WITH_FINDINGS + 1))
            TOTAL_FAILED_CHECKS=$((TOTAL_FAILED_CHECKS + COUNT))
        else
            echo "RESULT : No failed checks detected"
            echo "COUNT  : 0"
        fi

        echo "SAVED  : $JSON"

    else
        echo "RESULT : No JSON result generated"
    fi

    echo ""

done

echo "============================================================"
echo "                  CHECKOV SUMMARY"
echo "============================================================"
echo "Cases scanned         : $TOTAL"
echo "Cases with findings   : $CASES_WITH_FINDINGS"
echo "Cases with no findings: $((TOTAL - CASES_WITH_FINDINGS))"
echo "Total failed checks   : $TOTAL_FAILED_CHECKS"
echo "============================================================"
echo ""
