#!/bin/bash

set -u

INPUT_DIR="dataset/independent/iacsecbench"
OUTPUT_DIR="results/independent/iacsecbench"

KICS_DIR="$OUTPUT_DIR/kics"
TRIVY_DIR="$OUTPUT_DIR/trivy"
CHECKOV_DIR="$OUTPUT_DIR/checkov"

mkdir -p "$KICS_DIR"
mkdir -p "$TRIVY_DIR"
mkdir -p "$CHECKOV_DIR"

echo "=============================================="
echo "IaCSecBench External Corpus Scanner"
echo "=============================================="
echo "Input : $INPUT_DIR"
echo "Output: $OUTPUT_DIR"
echo

# Check required tools
command -v trivy >/dev/null 2>&1 || {
    echo "ERROR: Trivy is not installed or not in PATH."
    exit 1
}

command -v checkov >/dev/null 2>&1 || {
    echo "ERROR: Checkov is not installed or not in PATH."
    exit 1
}

# Check input directory
if [ ! -d "$INPUT_DIR" ]; then
    echo "ERROR: Input directory does not exist:"
    echo "$INPUT_DIR"
    exit 1
fi

repo_count=0
kics_success=0
trivy_success=0
checkov_success=0

for repo in "$INPUT_DIR"/*; do

    if [ ! -d "$repo" ]; then
        continue
    fi

    repo_id=$(basename "$repo")

    repo_count=$((repo_count + 1))

    echo
    echo "=============================================="
    echo "Repository: $repo_id"
    echo "=============================================="

    # ------------------------------------------------
    # KICS
    # ------------------------------------------------

    echo
    echo "[1/3] Running KICS..."

    mkdir -p "$KICS_DIR/$repo_id"

    if docker run --rm \
    -v "$(realpath "$repo"):/src:ro" \
    -v "$(realpath "$KICS_DIR/$repo_id"):/output" \
    checkmarx/kics:latest scan \
    -p /src \
    --report-formats json \
    --output-path /output \
    > "$KICS_DIR/$repo_id/console.log" 2>&1
    then
        echo "KICS: SUCCESS"
        kics_success=$((kics_success + 1))
    else
        echo "KICS: FAILED"
    fi

    # ------------------------------------------------
    # Trivy
    # ------------------------------------------------

    echo
    echo "[2/3] Running Trivy..."

    mkdir -p "$TRIVY_DIR/$repo_id"

    if trivy config \
        --misconfig-scanners terraform \
        --format json \
        --output "$TRIVY_DIR/$repo_id/results.json" \
        "$repo" \
        > "$TRIVY_DIR/$repo_id/console.log" 2>&1
    then
        echo "Trivy: SUCCESS"
        trivy_success=$((trivy_success + 1))
    else
        echo "Trivy: FAILED"
    fi

    # ------------------------------------------------
    # Checkov
    # ------------------------------------------------

    echo
    echo "[3/3] Running Checkov..."

    mkdir -p "$CHECKOV_DIR/$repo_id"

    if checkov \
        -d "$repo" \
        -o json \
        --output-file-path "$CHECKOV_DIR/$repo_id/results.json" \
        > "$CHECKOV_DIR/$repo_id/console.log" 2>&1
    then
        echo "Checkov: SUCCESS"
        checkov_success=$((checkov_success + 1))
    else
        echo "Checkov: FAILED"
    fi

done

echo
echo "=============================================="
echo "SCAN COMPLETE"
echo "=============================================="

echo "Repositories found : $repo_count"
echo "KICS successful     : $kics_success"
echo "Trivy successful    : $trivy_success"
echo "Checkov successful  : $checkov_success"

echo
echo "Results:"
echo "  KICS    : $KICS_DIR"
echo "  Trivy   : $TRIVY_DIR"
echo "  Checkov : $CHECKOV_DIR"

echo
echo "=============================================="