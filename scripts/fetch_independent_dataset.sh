#!/usr/bin/env bash
# Re-clones the 25 IaCSecBench independent repositories listed in
# dataset/independent/MANIFEST.csv into dataset/independent/iacsecbench/.
#
# The repository source is not vendored in version control (only the
# scanner output under results/independent/ is), so this script must be
# run before experiment/scripts/analyze_iacsecbench.py can recompute
# Terraform file/LOC/resource/module statistics.
set -euo pipefail

cd "$(dirname "$0")/.."

MANIFEST="dataset/independent/MANIFEST.csv"
DEST="dataset/independent/iacsecbench"

tail -n +2 "$MANIFEST" | while IFS=, read -r local_dir org repo url; do
    [ -z "$local_dir" ] && continue
    target="$DEST/$local_dir"
    if [ -d "$target/.git" ]; then
        echo "SKIP (already present): $local_dir"
        continue
    fi
    echo "Cloning $org/$repo -> $target"
    rm -rf "$target"
    git clone --depth 1 "$url" "$target"
done

echo "Done. Re-run: python3 experiment/scripts/analyze_iacsecbench.py"
