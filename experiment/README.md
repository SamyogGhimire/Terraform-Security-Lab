# Terraform Security Validation Experiment

## Purpose

Evaluate the ability of KICS, Trivy, and Checkov to detect known Terraform security misconfigurations.

## Dataset

Synthetic vulnerable cases:
- S01 — Public S3 access
- S02 — Unrestricted SSH security group
- S03 — Excessive IAM privileges
- S04 — Unsecured RDS
- S05 — Unencrypted S3
- S06 — Public S3 write access
- S07 — Unrestricted RDP security group
- S08 — Dangerous IAM PassRole
- S09 — Excessive Lambda IAM privileges
- S10 — Public/unprotected RDS

Secure baseline cases B01-B10 mirror each S-case's category with the
vulnerability remediated, and are used to evaluate false-positive behavior.

## Ground Truth

`experiment/data/ground_truth.csv` is the authoritative source read by
`experiment/scripts/build_matrix.py`. `dataset/ground_truth.csv` is kept as
an identical copy at the dataset root; if you edit one, copy it to the
other so they don't drift apart again.

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
