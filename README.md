# Terraform Security Validation Lab

Small technical prototype for the Terraform security-validation research.

It contains four intentionally insecure cases and one secure baseline, then runs Terraform validation, Checkov, Trivy, KICS (if installed), and a custom cross-resource IAM correlation check.

## Run

```bash
chmod +x run.sh
./run.sh
```

No AWS deployment is required.

## Why this is useful for the research

The prototype demonstrates a multi-layer workflow and, importantly, adds a custom correlation check for the combination of `iam:PassRole` and `ec2:RunInstances`. We will use actual scanner output rather than inventing results.

## Later extension

We can add an HTML dashboard, result normalisation, ground-truth CSV, timing measurements, and additional Terraform cases after the first run succeeds.
