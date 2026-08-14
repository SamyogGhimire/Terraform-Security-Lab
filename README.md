# Terraform Security Lab

A reproducible experimental framework for evaluating **KICS, Trivy, and Checkov** for Terraform Infrastructure-as-Code (IaC) security misconfiguration detection.

## Research Objective

The project investigates whether combining multiple IaC security scanners provides broader detection coverage than relying on a single scanner.

The evaluation uses:

- **10 synthetic vulnerable Terraform cases (S01-S10)**
- **10 secure baseline cases (B01-B10)**
- **5 public Terraform projects (P01-P05)**
- Ground-truth validation
- Precision, recall, F1-score and false-positive-rate analysis
- Scanner complementarity analysis
- Custom cross-resource IAM analysis

---

## Repository Structure

```text
.
├── dataset/
│   ├── synthetic/          # Controlled vulnerable Terraform cases
│   ├── secure/             # Secure baseline cases
│   └── public/             # External Terraform projects
│
├── experiment/
│   ├── generated/          # CSV/TXT experiment outputs
│   ├── graphs/             # Final experiment graphs
│   ├── public_dataset/     # Public corpus analysis
│   ├── results/            # Calculated metrics
│   └── scripts/            # Analysis and plotting scripts
│
├── results/
│   ├── kics/               # KICS raw JSON results
│   ├── trivy/              # Trivy raw JSON results
│   ├── checkov/            # Checkov raw JSON results
│   ├── public/              # Public-corpus scanner results
│   └── custom-iam.txt      # Cross-resource IAM analysis
│
├── scripts/
│   ├── run_kics.sh
│   ├── run_trivy.sh
│   └── run_checkov.sh
│
└── README.md
```

---

# 1. Experimental Dataset

## Synthetic Corpus

The synthetic corpus contains ten deliberately vulnerable Terraform configurations.

| Case | Target vulnerability |
|---|---|
| S01 | Public S3 access |
| S02 | Unrestricted SSH security group |
| S03 | Excessive IAM privileges |
| S04 | Unsecured RDS |
| S05 | Unencrypted S3 |
| S06 | Public S3 write access |
| S07 | Unrestricted RDP security group |
| S08 | Dangerous IAM PassRole |
| S09 | Excessive Lambda IAM privileges |
| S10 | Public/unprotected RDS |

Each case has an explicit ground-truth label.

## Secure Baseline Corpus

B01-B10 represent configurations intended to be secure. They are used to evaluate false-positive behaviour.

## Public Corpus

Five external Terraform projects are included:

```text
P01
P02
P03
P04
P05
```

The projects originate from the `galcan/terraform_sec` dataset. Original dataset metadata is retained in each project's `source.txt`.

The public corpus is treated as an **external validation corpus**, rather than being mixed directly into the controlled ground-truth benchmark.

---

# 2. Security Scanners

| Tool | Purpose |
|---|---|
| KICS | IaC security and compliance scanning |
| Trivy | Terraform/IaC misconfiguration scanning |
| Checkov | IaC policy and security scanning |
| Combined framework | Union of detections/findings across scanners |

KICS is executed through Docker in the supplied script.

---

# 3. Running the Scanners

From the repository root:

```bash
./scripts/run_kics.sh
./scripts/run_trivy.sh
./scripts/run_checkov.sh
```

Raw results are saved under:

```text
results/
```

Controlled results are separated into:

```text
results/kics/
results/trivy/
results/checkov/
```

Public-corpus results are stored under:

```text
results/public/
```

---

# 4. Experiment Analysis

The main analysis scripts are:

```bash
python3 experiment/scripts/generate_all_results.py
python3 experiment/scripts/calculate_final_metrics.py
python3 experiment/scripts/plot_final_metrics.py
```

Important generated files include:

```text
experiment/generated/detection_matrix.csv
experiment/generated/tool_metrics.csv
experiment/generated/final_results.csv
experiment/generated/finding_counts.csv
experiment/generated/combined_metrics.txt
experiment/generated/final_experiment_summary.txt
experiment/generated/public_dataset_results.csv
experiment/generated/public_findings.csv
```

---

# 5. Detection Matrix

The controlled experiment produces:

```text
experiment/generated/detection_matrix.csv
```

The matrix records target-vulnerability detection for each scanner.

```text
1 = detected
0 = not detected
```

Example:

```text
case_id,corpus,target_vulnerability,ground_truth,KICS,Trivy,Checkov
S01,synthetic,public_s3_access,1,1,1,1
S02,synthetic,unrestricted_ssh_security_group,1,1,1,1
...
```

The ground truth is used to distinguish correct detection from missed detection.

---

# 6. Final Controlled Benchmark

The current controlled benchmark contains:

- 10 vulnerable synthetic cases
- 10 secure baseline cases

The target-vulnerability detection results are:

| Tool | Vulnerable cases detected |
|---|---:|
| KICS | 9/10 |
| Trivy | 9/10 |
| Checkov | 10/10 |
| Combined | 10/10 |

The combined framework takes the union of scanner detections. It therefore provides coverage at least as broad as the individual scanners for the evaluated target vulnerabilities.

**Important:** scanner finding counts are not equivalent to target-vulnerability detection accuracy. A scanner can report additional security or compliance issues that are outside the experiment's target vulnerability.

---

# 7. Evaluation Metrics

The framework evaluates:

### Precision

```text
Precision = TP / (TP + FP)
```

### Recall

```text
Recall = TP / (TP + FN)
```

### F1-score

```text
F1 = 2 × Precision × Recall / (Precision + Recall)
```

### False Positive Rate

```text
FPR = FP / (FP + TN)
```

Where:

- **TP** = vulnerable case correctly detected
- **FP** = secure baseline incorrectly flagged
- **TN** = secure baseline correctly left undetected
- **FN** = vulnerable case missed

The current generated metric artefacts are available in:

```text
experiment/generated/tool_metrics.csv
experiment/generated/final_results.csv
experiment/results/tool_metrics.csv
```

---

# 8. Final Graphs

All experiment graphs are kept in:

```text
experiment/graphs/
```

## Overall Tool Performance

![Final Tool Performance](experiment/graphs/final_tool_performance.png)

## Detection Comparison

![Detection Comparison](experiment/graphs/detection_comparison.png)

## Precision

![Precision](experiment/graphs/precision_final.png)

## Recall

![Recall](experiment/graphs/recall_final.png)

## F1 Score

![F1 Score](experiment/graphs/f1_final.png)

## False Positive Rate

![False Positive Rate](experiment/graphs/fpr_final.png)

## Scanner Complementarity

![Scanner Complementarity](experiment/graphs/scanner_complementarity.png)

## Unique Detection Contribution

![Unique Detection Contribution](experiment/graphs/unique_detection_contribution.png)

## Vulnerable vs Baseline

![Vulnerable vs Baseline](experiment/graphs/vulnerable_vs_baseline.png)

## Findings by Case

![Findings by Case](experiment/graphs/findings_by_case.png)

---

# 9. Public Dataset Validation

The public corpus is analysed separately because complete ground truth is not available for every finding.

The available projects are:

```text
dataset/public/P01
dataset/public/P02
dataset/public/P03
dataset/public/P04
dataset/public/P05
```

Scanner outputs:

```text
results/public/kics/
results/public/trivy/
results/public/checkov/
```

Generated public-dataset analysis:

```text
experiment/generated/public_dataset_results.csv
experiment/generated/public_findings.csv
experiment/generated/public_validation.csv
experiment/generated/public/
```

Public-corpus graphs include:

![Public Findings by Case](experiment/graphs/public_findings_by_case.png)

![Public Scanner Comparison](experiment/graphs/public_scanner_comparison.png)

![Public Scanner Findings](experiment/graphs/public_scanner_findings.png)

![Public Average Findings](experiment/graphs/public_average_findings.png)

The public corpus demonstrates that different scanners report different security findings for the same Terraform projects, supporting the investigation of scanner complementarity.

---

# 10. Scanner Complementarity

Different scanners use different rule sets, policies, resource coverage and security heuristics.

Therefore, two scanners can analyse the same Terraform project and produce different findings.

The framework considers:

```text
Individual detection
        +
False-positive behaviour
        +
Finding overlap
        +
Unique detection contribution
        =
Multi-scanner security coverage
```

The combined framework uses the union of detections rather than assuming that one scanner is a complete security oracle.

---

# 11. Cross-Resource IAM Analysis

The repository also includes a custom analysis:

```text
results/custom-iam.txt
```

This addresses security relationships that can span multiple Terraform resources.

One evaluated example combines:

```text
iam:PassRole
+
ec2:RunInstances
```

to identify a potential privilege-escalation path.

This complements conventional single-resource scanner rules.

---

# 12. Reproducibility

A typical reproduction workflow is:

```bash
git clone <repository>
cd terraform-security-lab

./scripts/run_kics.sh
./scripts/run_trivy.sh
./scripts/run_checkov.sh

python3 experiment/scripts/generate_all_results.py
python3 experiment/scripts/calculate_final_metrics.py
python3 experiment/scripts/plot_final_metrics.py
```

Generated artefacts are placed in:

```text
experiment/generated/
experiment/graphs/
```

Scanner versions should be recorded when reproducing the experiment because rule sets and findings can change between releases.

---

# 13. Interpretation

The project distinguishes between two different measurements:

### Target-vulnerability detection

Whether a scanner detects the vulnerability explicitly defined by the experiment's ground truth.

### Security finding volume

The total number of security/compliance findings reported by a scanner.

These must not be treated as the same metric.

For example, a scanner can report:

- missing logging;
- missing tags;
- encryption recommendations;
- missing descriptions;
- monitoring recommendations;
- IAM policy concerns;

without necessarily detecting the specific target vulnerability.

Therefore:

> **Finding count alone should not be interpreted as detection accuracy.**

---

# 14. Limitations

The current experiment has several limitations:

1. The controlled benchmark is relatively small.
2. The public validation corpus contains five projects.
3. Scanner rule sets change between releases.
4. Different scanners can classify the same underlying weakness differently.
5. Public projects do not provide complete ground truth for every finding.
6. Static analysis cannot prove runtime exploitability for every finding.
7. The combined framework currently uses scanner-result union rather than a learned ensemble model.

---

# 15. Future Work

Potential extensions include:

- expanding the public Terraform corpus;
- adding more vulnerability classes;
- evaluating additional scanners;
- version-controlled scanner benchmarking;
- duplicate-finding normalisation;
- severity-weighted scoring;
- automated cross-resource dependency analysis;
- runtime validation of selected findings;
- CI/CD integration;
- SARIF-based result aggregation;
- larger-scale statistical evaluation.

---

# 16. Research Contribution

The implemented workflow provides a reproducible multi-layer validation approach:

```text
Terraform IaC
      |
      +---- KICS
      |
      +---- Trivy
      |
      +---- Checkov
      |
      +---- Custom cross-resource analysis
      |
      v
Security findings
      |
      v
Ground-truth validation
      |
      v
Precision / Recall / F1 / FPR
      |
      v
Complementarity analysis
      |
      v
Combined security coverage
```

The main conclusion supported by the experiment is that **multi-tool IaC security validation can provide broader coverage than relying on a single scanner**, while requiring explicit ground truth and careful false-positive analysis.

---

## Project Status

**Research experiment and analysis complete.**

The repository contains the datasets, raw scanner outputs, ground-truth data, experiment scripts, generated metrics, graphs, public-dataset validation, and custom cross-resource IAM analysis required to reproduce the reported evaluation.