#!/bin/bash

set -e

mkdir -p results/kics

echo ""
echo "============================================================"
echo "              KICS TERRAFORM SECURITY SCAN"
echo "============================================================"
echo ""

TOTAL=0
CASES_WITH_FINDINGS=0
TOTAL_FINDINGS=0

for dir in dataset/synthetic/* dataset/secure/*; do

    case_id=$(basename "$dir")
    TOTAL=$((TOTAL + 1))

    echo "------------------------------------------------------------"
    echo "CASE: $case_id"
    echo "TARGET: $dir"
    echo "------------------------------------------------------------"

    mkdir -p "results/kics/$case_id"

    docker run --rm \
        -v "$(pwd)/$dir:/path" \
        -v "$(pwd)/results/kics/$case_id:/results" \
        checkmarx/kics:latest \
        scan \
        -p /path \
        --report-formats json \
        --output-path /results \
        --output-name "$case_id" \
        >/dev/null 2>&1

    JSON="results/kics/$case_id/$case_id.json"

    if [ -f "$JSON" ]; then

        COUNT=$(python3 - "$JSON" <<'PY'
import json
import sys

with open(sys.argv[1]) as f:
    data = json.load(f)

count = 0

for query in data.get("queries", []):
    count += query.get("total_counter", 0)

print(count)
PY
)

        if [ "$COUNT" -gt 0 ]; then
            echo "RESULT : Findings detected"
            echo "COUNT  : $COUNT"
            CASES_WITH_FINDINGS=$((CASES_WITH_FINDINGS + 1))
            TOTAL_FINDINGS=$((TOTAL_FINDINGS + COUNT))
        else
            echo "RESULT : No findings detected"
            echo "COUNT  : 0"
        fi

        echo "SAVED  : $JSON"

    else
        echo "ERROR  : JSON result was not generated"
    fi

    echo ""

done

echo "============================================================"
echo "                    KICS SUMMARY"
echo "============================================================"
echo "Cases scanned        : $TOTAL"
echo "Cases with findings  : $CASES_WITH_FINDINGS"
echo "Cases with no findings: $((TOTAL - CASES_WITH_FINDINGS))"
echo "Total findings       : $TOTAL_FINDINGS"
echo "============================================================"
echo ""
