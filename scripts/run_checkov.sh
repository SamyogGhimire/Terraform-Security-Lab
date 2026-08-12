#!/bin/bash

set -e

mkdir -p results/checkov

for dir in dataset/synthetic/* dataset/secure/*; do

    case_id=$(basename "$dir")

    echo ""
    echo "========== $case_id =========="

    mkdir -p "results/checkov/$case_id"

    checkov -d "$dir" \
        --output json \
        --output-file-path "results/checkov/$case_id"

    echo "Finished $case_id"

done
