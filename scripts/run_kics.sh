#!/bin/bash

mkdir -p results/kics

echo ""
echo "============================================================"
echo "              KICS TERRAFORM SECURITY SCAN"
echo "============================================================"
echo ""

TOTAL=0
CASES_WITH_FINDINGS=0
CASES_WITHOUT_FINDINGS=0
FAILED_SCANS=0
TOTAL_FINDINGS=0

for dir in dataset/synthetic/* dataset/secure/* dataset/public/*; do

    # Skip anything that is not a directory
    [ -d "$dir" ] || continue

    case_id=$(basename "$dir")
    TOTAL=$((TOTAL + 1))

    echo "------------------------------------------------------------"
    echo "CASE:   $case_id"
    echo "TARGET: $dir"
    echo "------------------------------------------------------------"

    mkdir -p "results/kics/$case_id"

    JSON="results/kics/$case_id/$case_id.json"

    # Remove old result so we know this scan generated the file
    rm -f "$JSON"

    echo "Running KICS..."

    if docker run --rm \
        -v "$(pwd)/$dir:/path:ro" \
        -v "$(pwd)/results/kics/$case_id:/results" \
        checkmarx/kics:latest \
        scan \
        -p /path \
        --report-formats json \
        --output-path /results \
        --output-name "$case_id"
    then

        if [ -f "$JSON" ]; then

            COUNT=$(python3 - "$JSON" <<'PY'
import json
import sys

path = sys.argv[1]

with open(path) as f:
    data = json.load(f)

print(data.get("total_counter", 0))
PY
)

            if [ "$COUNT" -gt 0 ]; then
                echo ""
                echo "RESULT : FINDINGS DETECTED"
                echo "COUNT  : $COUNT"

                CASES_WITH_FINDINGS=$((CASES_WITH_FINDINGS + 1))
                TOTAL_FINDINGS=$((TOTAL_FINDINGS + COUNT))

            else
                echo ""
                echo "RESULT : NO FINDINGS"
                echo "COUNT  : 0"

                CASES_WITHOUT_FINDINGS=$((CASES_WITHOUT_FINDINGS + 1))
            fi

            echo "SAVED  : $JSON"

        else

            echo ""
            echo "ERROR  : KICS completed but JSON was not generated"
            echo "EXPECTED: $JSON"

            FAILED_SCANS=$((FAILED_SCANS + 1))
        fi

    else

        echo ""
        echo "ERROR  : KICS scan FAILED for $case_id"

        FAILED_SCANS=$((FAILED_SCANS + 1))
    fi

    echo ""

done

echo "============================================================"
echo "                    KICS SUMMARY"
echo "============================================================"
echo "Cases attempted       : $TOTAL"
echo "Cases with findings   : $CASES_WITH_FINDINGS"
echo "Cases with no findings: $CASES_WITHOUT_FINDINGS"
echo "Failed scans          : $FAILED_SCANS"
echo "Total findings        : $TOTAL_FINDINGS"
echo "============================================================"
echo ""
