# Scanner Versions

Static-analysis rule sets change frequently, so the exact TP/TN/FP/FN counts
in this repository are only reproducible against the scanner versions below.
Re-running the scans with newer KICS/Trivy/Checkov releases will likely
change individual case outcomes (new or removed rules) even if nothing in
the Terraform source changes.

| Scanner | Version | How it was confirmed |
|---|---|---|
| KICS | v2.1.20 | Embedded in every `kics_version` field across all 20 controlled-case result files and all 25 independent-dataset result files (`results/**/*.json`) |
| Checkov | 3.3.9 | Embedded in every `summary.checkov_version` field across the controlled and independent result files |
| Trivy | 0.52.2 | Trivy's JSON output does not embed its own version number, so this is the version installed in the environment that produced `results/trivy/`. The scan timestamps recorded in each file's `CreatedAt` field are 2026-08-13. |
| Terraform | v1.15.8 | Used only to initialize providers for scanning; not itself part of the detection pipeline |

## Reproducing with these exact versions

```bash
# Trivy
# (install the specific release: https://github.com/aquasecurity/trivy/releases/tag/v0.52.2)

# Checkov
pip install checkov==3.3.9

# KICS (via Docker, pinned instead of :latest)
docker pull checkmarx/kics:v2.1.20
```

If you re-run the scanners with different versions, regenerate
`experiment/results/detection_matrix.csv` and
`experiment/data/ground_truth.csv`-backed metrics via
`experiment/scripts/build_matrix.py` and re-verify each case's target-vulnerability
detection manually — the hardcoded 0/1 values in `build_matrix.py` reflect a
manual reading of the 2026-08-13 scan output, not an automated comparison the
script can re-derive from newer scans by itself.
