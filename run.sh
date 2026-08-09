#!/usr/bin/env bash
set -u
ROOT="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$ROOT/results/kics"
for dir in "$ROOT"/cases/*; do
  echo "=== $(basename "$dir") ==="
  terraform -chdir="$dir" fmt -check || true
  terraform -chdir="$dir" init -backend=false -input=false >/dev/null 2>&1 || true
  terraform -chdir="$dir" validate || true
done
if command -v checkov >/dev/null 2>&1; then checkov -d "$ROOT/cases" -o json > "$ROOT/results/checkov.json" || true; else echo 'Checkov not installed'; fi
if command -v trivy >/dev/null 2>&1; then trivy config --format json --output "$ROOT/results/trivy.json" "$ROOT/cases" || true; else echo 'Trivy not installed'; fi
if command -v kics >/dev/null 2>&1; then kics scan -p "$ROOT/cases" -o "$ROOT/results/kics" --report-formats json || true; else echo 'KICS not installed'; fi
python3 "$ROOT/scripts/cross_resource_check.py" | tee "$ROOT/results/custom-iam.txt"
echo "Results are in $ROOT/results/"
