# Terraform Security Validation Experiment

## Purpose

Evaluate the ability of KICS, Trivy, and Checkov to detect known Terraform security misconfigurations.

## Dataset

Synthetic vulnerable cases:
- S01 — Public S3
- S02 — Open SSH
- S03 — Excessive IAM
- S04 — Hardcoded Credentials
- S05 — Missing Encryption

Secure baseline cases:
- B01 — Secure S3
- B02 — Secure SSH configuration
- B03 — Secure IAM configuration
- B04 — No hardcoded credentials
- B05 — Encryption enabled

## Ground Truth

ground_truth.csv defines whether each case contains the target vulnerability.

## Scanner Results

### KICS
Stored under:
results/kics/

### Trivy
Stored under:
results/trivy/

### Checkov
Stored under:
results/checkov/

## Metrics

The experiment will calculate:

- True Positive (TP)
- True Negative (TN)
- False Positive (FP)
- False Negative (FN)
- Precision
- Recall
- F1-score
- False Positive Rate
- Detection Coverage
- Tool Overlap

## Important

Raw scanner finding counts are not treated as TP/FP directly.

A finding is counted as a detection only when it corresponds to the target vulnerability defined in the ground truth.
