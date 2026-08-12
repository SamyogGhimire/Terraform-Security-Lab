for dir in dataset/synthetic/* dataset/secure/*; do
    case_id=$(basename "$dir")
    echo "========== $case_id =========="
    mkdir -p "results/kics/$case_id"

    docker run --rm \
        -v "$(pwd)/$dir:/path" \
        -v "$(pwd)/results/kics/$case_id:/results" \
        checkmarx/kics:latest \
        scan -p /path \
        --report-formats json \
        --output-path /results \
        --output-name "$case_id"

    echo "Finished $case_id"
done