# Terraform Security Validation Lab

A small, reproducible technical prototype for the **Terraform Infrastructure-as-Code (IaC) security validation research project**.

The project investigates whether using multiple security scanners together can improve detection of intentionally introduced Terraform security misconfigurations.

The prototype uses three IaC security scanners:

- **KICS**
- **Trivy**
- **Checkov**

It also contains a small **custom cross-resource IAM correlation check** for security conditions that may depend on relationships between resources rather than a single resource configuration.

---

## 1. Project Goal

The main idea is simple:

> Create a small set of known Terraform security cases, scan them with multiple tools, compare their results against known ground truth, and measure how well each scanner and the combined approach performs.

The experiment deliberately avoids requiring a real AWS deployment.

This makes the prototype:

- easy to reproduce;
- inexpensive;
- safe to run;
- suitable for a university research demonstration;
- easier to understand than a large cloud deployment.

---

## 2. Basic Workflow

```text
Terraform test cases
        |
        v
+-----------------------+
| Ground-truth cases    |
| S01-S05 / B01-B05     |
+-----------------------+
        |
        v
+-------------------------------+
| Security validation scanners  |
| KICS | Trivy | Checkov        |
+-------------------------------+
        |
        v
Raw JSON / scanner results
        |
        v
Result normalisation
        |
        v
Detection matrix
        |
        v
+------------------------------------+
| Metrics                            |
| TP / TN / FP / FN                  |
| Precision / Recall / F1 / Accuracy |
| FPR                                |
+------------------------------------+
        |
        v
Complementarity analysis
        |
        v
Combined multi-scanner result
```

---

## 3. Repository Structure

A simplified structure is:

```text
terraform-security-lab/
│
├── dataset/
│   ├── synthetic/
│   │   ├── S01/
│   │   ├── S02/
│   │   ├── S03/
│   │   ├── S04/
│   │   └── S05/
│   │
│   └── secure/
│       ├── B01/
│       ├── B02/
│       ├── B03/
│       ├── B04/
│       └── B05/
│
├── results/
│   ├── kics/
│   ├── trivy/
│   └── checkov/
│
├── experiment/
│   ├── detection_matrix.csv
│   ├── tool_metrics.py
│   ├── combined_metrics.py
│   ├── complementarity.py
│   └── ...
│
├── scripts/
│   └── run_kics.sh
│
└── run.sh
```

The exact repository may contain additional helper files.

---

# 4. The Terraform Test Cases

The experiment uses two groups.

## Vulnerable cases

The synthetic cases are:

| Case | Vulnerability |
|---|---|
| S01 | Public S3 access |
| S02 | Unrestricted security group |
| S03 | Excessive IAM privileges |
| S04 | Unsecured RDS |
| S05 | Unencrypted S3 |

These cases intentionally contain a known security problem.

Therefore:

```text
ground_truth = 1
```

---

## Secure baseline cases

The baseline cases are:

| Case | Intended configuration |
|---|---|
| B01 | Secure S3 |
| B02 | Restricted security group |
| B03 | Limited IAM policy |
| B04 | Secure RDS password handling |
| B05 | Encrypted S3 |

These cases are intended to represent configurations where the target vulnerability is absent.

Therefore:

```text
ground_truth = 0
```

The baseline cases are important because they allow us to measure false positives rather than only measuring whether scanners find vulnerabilities.

---

# 5. S01 – Public S3 Access

File:

```text
dataset/synthetic/S01/main.tf
```

The case creates an S3 bucket and deliberately disables public-access protections.

Important configuration:

```hcl
block_public_acls       = false
block_public_policy     = false
ignore_public_acls      = false
restrict_public_buckets = false
```

It also creates a bucket policy with:

```hcl
Effect    = "Allow"
Principal = "*"
Action    = "s3:GetObject"
```

### What does this mean?

`Principal = "*"` means any principal can potentially access the resource, while the policy allows object retrieval.

This creates a public-access security problem.

### Ground truth

```text
S01 = vulnerable
ground_truth = 1
```

### Observed detection

| Tool | Detected? |
|---|---:|
| KICS | Yes |
| Trivy | No |
| Checkov | Yes |

This is one example of **scanner complementarity**: KICS and Checkov detected the target case while Trivy did not.

---

# 6. S02 – Unrestricted Security Group

File:

```text
dataset/synthetic/S02/main.tf
```

The security group allows SSH from:

```hcl
cidr_blocks = ["0.0.0.0/0"]
```

Port:

```hcl
from_port = 22
to_port   = 22
```

This means SSH is exposed to the entire IPv4 internet.

The egress rule also permits unrestricted outbound traffic.

### Ground truth

```text
S02 = vulnerable
ground_truth = 1
```

### Detection

All three scanners detected the target vulnerability:

| Tool | Detected? |
|---|---:|
| KICS | Yes |
| Trivy | Yes |
| Checkov | Yes |

---

# 7. S03 – Excessive IAM Privileges

File:

```text
dataset/synthetic/S03/main.tf
```

The IAM policy contains:

```hcl
Effect   = "Allow"
Action   = "*"
Resource = "*"
```

This is intentionally excessive.

It gives the policy broad permissions over all actions and resources.

### Ground truth

```text
S03 = vulnerable
ground_truth = 1
```

### Detection

| Tool | Detected? |
|---|---:|
| KICS | Yes |
| Trivy | No |
| Checkov | Yes |

Again, the result demonstrates why multiple scanners can be useful.

---

# 8. S04 – Unsecured RDS

File:

```text
dataset/synthetic/S04/main.tf
```

The RDS instance contains a hard-coded password:

```hcl
password = "SuperSecretPassword123!"
```

It also lacks several security controls such as encryption and stronger database protection settings.

### Ground truth

```text
S04 = vulnerable
ground_truth = 1
```

### Detection

All three scanners detected the target case:

| Tool | Detected? |
|---|---:|
| KICS | Yes |
| Trivy | Yes |
| Checkov | Yes |

---

# 9. S05 – Unencrypted S3

File:

```text
dataset/synthetic/S05/main.tf
```

The bucket is created without a server-side encryption configuration.

### Ground truth

```text
S05 = vulnerable
ground_truth = 1
```

### Detection

| Tool | Detected? |
|---|---:|
| KICS | No |
| Trivy | Yes |
| Checkov | No |

This is an important result because **Trivy detected the target vulnerability that KICS and Checkov missed**.

This provides direct evidence of scanner complementarity.

---

# 10. Secure Baselines

The baseline cases are designed to represent the absence of the target vulnerability.

For example, B01 contains an S3 public-access block:

```hcl
block_public_acls       = true
block_public_policy     = true
ignore_public_acls      = true
restrict_public_buckets = true
```

B02 restricts SSH to:

```hcl
cidr_blocks = ["10.0.0.0/16"]
```

B03 limits IAM access to:

```hcl
Action   = ["s3:GetObject"]
Resource = "arn:aws:s3:::example-bucket/*"
```

B04 uses a sensitive Terraform variable for the database password:

```hcl
variable "db_password" {
  type      = string
  sensitive = true
}
```

B05 configures S3 server-side encryption using AES256.

The purpose of these cases is to check whether the scanners incorrectly report the target vulnerability when it is not present.

---

# 11. Running the Project

The original prototype can be started with:

```bash
chmod +x run.sh
./run.sh
```

No AWS deployment is required for the scanner experiment.

The scanners analyse Terraform configuration files rather than requiring the infrastructure to actually exist in AWS.

---

# 12. KICS

KICS was run using Docker.

Example:

```bash
docker run --rm -t \
-v "$(pwd)/dataset/synthetic/S01:/path" \
checkmarx/kics:latest \
scan -p /path
```

For reproducible JSON output, the project uses an output directory:

```bash
docker run --rm -t \
-v "$(pwd)/$dir:/path" \
-v "$(pwd)/results/kics/$case_id:/results" \
checkmarx/kics:latest \
scan \
-p /path \
--report-formats json \
--output-path /results \
--output-name "$case_id"
```

This stores machine-readable results under:

```text
results/kics/
```

For example:

```text
results/kics/S01/S01.json
```

The KICS JSON contains information such as:

- severity;
- query name;
- CWE;
- risk score;
- affected files;
- query ID;
- total findings;
- severity counters.

Example S01 summary:

```text
CRITICAL = 1
HIGH     = 1
MEDIUM   = 6
LOW      = 1
INFO     = 1

TOTAL = 10
```

---

# 13. Trivy

Trivy was used as another independent Terraform/IaC security scanner.

Its results were stored and then normalised into the experiment data.

The purpose is not to decide which tool is "best" from raw finding counts.

Instead, the important question is:

> Did the scanner detect the vulnerability that was intentionally introduced into the test case?

---

# 14. Checkov

Checkov was used as the third scanner.

Checkov analyses Terraform configuration against security and compliance checks.

Its findings were also normalised into the experiment data.

Again, the experiment focuses on whether the **target vulnerability** was detected rather than simply counting every warning produced by a scanner.

---

# 15. Why Raw Finding Counts Are Not Enough

A scanner can produce many findings without necessarily detecting the vulnerability being tested.

For example, one case may generate:

```text
10 findings
```

while another scanner generates:

```text
4 findings
```

That does not automatically mean the first scanner is better.

Some findings may be:

- informational;
- unrelated to the target vulnerability;
- best-practice recommendations;
- duplicate observations of related configuration issues.

Therefore, the experiment uses a **ground-truth detection matrix**.

---

# 16. Detection Matrix

The final detection matrix was:

```csv
case_id,corpus,target_vulnerability,ground_truth,KICS,Trivy,Checkov
S01,synthetic,public_s3_access,1,1,0,1
S02,synthetic,unrestricted_security_group,1,1,1,1
S03,synthetic,excessive_iam_privileges,1,1,0,1
S04,synthetic,unsecured_rds,1,1,1,1
S05,synthetic,unencrypted_s3,1,0,1,0
B01,baseline,secure_s3,0,0,0,0
B02,baseline,restricted_security_group,0,0,0,0
B03,baseline,limited_iam_policy,0,0,0,0
B04,baseline,secure_rds_password,0,0,0,0
B05,baseline,encrypted_s3,0,0,0,0
```

The values mean:

```text
1 = detected / vulnerable
0 = not detected / not vulnerable
```

---

# 17. Confusion Matrix

The metrics use four standard quantities.

| Term | Meaning |
|---|---|
| TP | Vulnerable case correctly detected |
| TN | Secure case correctly left undetected |
| FP | Secure case incorrectly reported as vulnerable |
| FN | Vulnerable case missed |

For example:

```text
S01:
Ground truth = 1
KICS = 1

=> TP for KICS
```

For B01:

```text
Ground truth = 0
KICS = 0

=> TN for KICS
```

---

# 18. Scanner Metrics

The experiment produced the following results.

| Metric | KICS | Trivy | Checkov |
|---|---:|---:|---:|
| TP | 4 | 3 | 4 |
| TN | 5 | 5 | 5 |
| FP | 0 | 0 | 0 |
| FN | 1 | 2 | 1 |
| Precision | 100.00% | 100.00% | 100.00% |
| Recall | 80.00% | 60.00% | 80.00% |
| F1-score | 88.89% | 75.00% | 88.89% |
| Accuracy | 90.00% | 80.00% | 90.00% |
| FPR | 0.00% | 0.00% | 0.00% |

### Interpretation

KICS and Checkov achieved:

```text
Recall = 80%
F1-score = 88.89%
Accuracy = 90%
```

Trivy achieved:

```text
Recall = 60%
F1-score = 75%
Accuracy = 80%
```

All three scanners achieved:

```text
Precision = 100%
FPR = 0%
```

within this small experiment.

The result should not be interpreted as proof that these scanners always have these performance levels. The dataset is intentionally small and controlled.

---

# 19. Scanner Metrics Graph

The following graph visualises the measured metrics:

![Scanner performance metrics](scanner_metrics.png)

The graph is generated from the observed experiment results.

---

# 20. Complementarity

The most interesting part of the experiment is not simply comparing the individual scores.

It is examining **which vulnerabilities each tool detects or misses**.

## S01

```text
Detected by: KICS, Checkov
Missed by:   Trivy
```

## S02

```text
Detected by: KICS, Trivy, Checkov
Missed by:   None
```

## S03

```text
Detected by: KICS, Checkov
Missed by:   Trivy
```

## S04

```text
Detected by: KICS, Trivy, Checkov
Missed by:   None
```

## S05

```text
Detected by: Trivy
Missed by:   KICS, Checkov
```

The S05 result is especially useful because it shows a vulnerability detected by Trivy but missed by the other two scanners.

---

# 21. Pairwise Complementarity

The measured pairwise results were:

| Scanner pair | Both detected | First only | Second only |
|---|---:|---:|---:|
| KICS vs Trivy | 2 | 2 | 1 |
| KICS vs Checkov | 4 | 0 | 0 |
| Trivy vs Checkov | 2 | 1 | 2 |

This shows that KICS and Checkov behaved very similarly for these five target vulnerabilities, while Trivy contributed unique detection on S05.

---

# 22. Combined Framework

The combined approach uses a simple rule:

```text
If ANY scanner detects the target vulnerability:
    Combined = 1
else:
    Combined = 0
```

In Boolean form:

```text
Combined = KICS OR Trivy OR Checkov
```

This is intentionally simple.

The objective is to demonstrate the basic benefit of combining independent scanners before developing more sophisticated correlation or weighting methods.

---

# 23. Combined Results

The combined framework produced:

| Metric | Combined framework |
|---|---:|
| TP | 5 |
| TN | 5 |
| FP | 0 |
| FN | 0 |
| Precision | 100.00% |
| Recall | 100.00% |
| F1-score | 100.00% |
| Accuracy | 100.00% |
| FPR | 0.00% |

Case-level result:

```text
S01 -> detected
S02 -> detected
S03 -> detected
S04 -> detected
S05 -> detected

B01 -> not detected
B02 -> not detected
B03 -> not detected
B04 -> not detected
B05 -> not detected
```

Therefore:

```text
Vulnerable cases = 5
Detected         = 5
Missed           = 0
Coverage         = 100%
```

---

# 24. Important Interpretation of the 100% Result

The 100% combined score should be presented carefully.

It does **not** mean:

> The proposed framework is guaranteed to detect every Terraform vulnerability.

It means:

> Within the five vulnerable cases and five secure baseline cases used in this controlled experiment, the OR-based combination of KICS, Trivy and Checkov detected all five target vulnerabilities and produced no false positives against the five baseline cases.

This distinction is important for academic reporting.

The dataset is small, so the result demonstrates the behaviour of the prototype rather than universal scanner effectiveness.

---

# 25. Finding-Level Results

The scanners produced different numbers of total findings.

| Tool | Vulnerable-case findings | Baseline findings | Total |
|---|---:|---:|---:|
| KICS | 38 | 25 | 63 |
| Trivy | 27 | 21 | 48 |
| Checkov | 40 | 24 | 64 |

Case-level counts:

| Case | KICS | Trivy | Checkov |
|---|---:|---:|---:|
| S01 | 10 | 8 | 12 |
| S02 | 9 | 5 | 4 |
| S03 | 5 | 0 | 9 |
| S04 | 10 | 5 | 8 |
| S05 | 4 | 9 | 7 |
| B01 | 4 | 4 | 6 |
| B02 | 7 | 4 | 3 |
| B03 | 2 | 0 | 0 |
| B04 | 8 | 5 | 8 |
| B05 | 4 | 8 | 7 |

These numbers show that scanners produce different quantities and types of findings even when analysing the same Terraform configuration.

---

# 26. Why the Finding Counts Differ

KICS, Trivy and Checkov use different:

- rule sets;
- security policies;
- query/check identifiers;
- severity classifications;
- detection logic;
- configuration assumptions.

Therefore, it is expected that they do not produce identical findings.

For the research, this difference is useful because it creates the opportunity to study **complementarity**.

---

# 27. Custom Cross-Resource IAM Check

The project also contains a custom correlation check.

The purpose is to identify a potentially dangerous relationship involving:

```text
iam:PassRole
```

and:

```text
ec2:RunInstances
```

Individually, each permission may not tell the complete security story.

Together, they can create a potentially significant privilege path.

The custom check therefore looks across resources and policies rather than treating every Terraform resource independently.

Example conceptual result:

```text
PassRole found
RunInstances found

=> Potential cross-resource privilege path
```

This is different from a normal single-resource rule.

---

# 28. Why Cross-Resource Analysis Matters

Traditional static IaC scanners often operate using individual checks.

However, some security problems depend on the relationship between multiple permissions or resources.

For example:

```text
IAM permission
      +
EC2 permission
      |
      v
Potential privilege path
```

This motivates the multi-layer design.

The prototype therefore has two levels:

### Layer 1 – Existing scanners

```text
KICS
Trivy
Checkov
```

### Layer 2 – Custom correlation

```text
Cross-resource IAM relationship analysis
```

The second layer is intended to demonstrate how a research framework can extend beyond the individual rule sets of existing scanners.

---

# 29. Reproducibility

The experiment is designed to be reproducible.

The main requirements are:

- Linux environment;
- Terraform;
- Docker;
- KICS container;
- Trivy;
- Checkov;
- Python 3.

The Terraform cases are local files.

No AWS deployment is required for the core scanning experiment.

---

# 30. Main Experiment Scripts

### Tool metrics

```bash
python3 experiment/tool_metrics.py
```

This calculates:

- TP;
- TN;
- FP;
- FN;
- precision;
- recall;
- F1-score;
- accuracy;
- false-positive rate.

---

### Combined metrics

```bash
python3 experiment/combined_metrics.py
```

This treats a target vulnerability as detected if at least one scanner detects it.

Conceptually:

```text
KICS OR Trivy OR Checkov
```

---

### Complementarity

```bash
python3 experiment/complementarity.py
```

This identifies:

- which scanners detect each vulnerable case;
- which scanners miss each case;
- pairwise overlap;
- scanner-specific detections;
- overall vulnerable-case coverage.

---

# 31. What the Experiment Demonstrates

The prototype demonstrates five main points.

### 1. Individual scanners have different detection coverage

KICS and Checkov achieved 80% recall in the controlled dataset.

Trivy achieved 60% recall.

### 2. No individual scanner detected every target vulnerability

Each scanner missed at least one vulnerable case.

### 3. Scanner outputs are complementary

For example:

```text
S05 -> Trivy detected it
       KICS missed it
       Checkov missed it
```

### 4. Combining scanners improved target-case coverage

The combined OR-based approach detected:

```text
5 / 5 vulnerable cases
```

### 5. Cross-resource checks can extend normal static scanning

The custom IAM correlation check demonstrates a second analysis layer.

---

# 32. Limitations

This is a **small technical prototype**, not a production benchmark.

Important limitations include:

1. Only five vulnerable cases are used for the main detection experiment.
2. Only five secure baseline cases are used for false-positive evaluation.
3. The cases are controlled rather than sampled randomly from a large corpus.
4. The combined detector uses a simple OR rule.
5. Scanner finding counts are not directly comparable as vulnerability counts.
6. The experiment does not measure runtime performance in the current results.
7. AWS infrastructure is not deployed as part of the core experiment.
8. The 100% combined result is therefore specific to this test set.

These limitations should be acknowledged in the research report.

---

# 33. Suggested Research Interpretation

A suitable interpretation is:

> The prototype indicates that different Terraform security scanners can exhibit complementary detection behaviour. While individual scanners missed some intentionally introduced vulnerabilities, combining their target-case detections resulted in complete coverage across the five vulnerable cases in this controlled dataset. The result provides preliminary evidence supporting a multi-layer validation approach, while the small dataset means that broader evaluation is required before generalising the findings.

---

# 34. Future Extensions

The prototype can later be extended with:

- larger public Terraform datasets;
- Kaggle or GitHub-derived IaC datasets;
- additional vulnerable configurations;
- more secure baselines;
- repeated experiments;
- runtime measurements;
- finding normalisation;
- duplicate finding detection;
- severity-weighted metrics;
- HTML dashboards;
- automated report generation;
- more cross-resource security rules;
- statistical analysis.

A larger dataset would make the evaluation more statistically meaningful.

---

# 35. Current Key Results

### Individual scanners

```text
KICS
Recall    = 80%
F1-score  = 88.89%
Accuracy  = 90%

Trivy
Recall    = 60%
F1-score  = 75%
Accuracy  = 80%

Checkov
Recall    = 80%
F1-score  = 88.89%
Accuracy  = 90%
```

### Combined approach

```text
Precision = 100%
Recall    = 100%
F1-score  = 100%
Accuracy  = 100%
FPR       = 0%
```

### Coverage

```text
5 vulnerable cases
5 detected
0 missed

Coverage = 100%
```

Again, these results apply only to the current controlled experiment.

---

# 36. Final Takeaway

The project is intentionally small.

The purpose is not to build a complicated security platform.

The purpose is to demonstrate a clear research workflow:

```text
Known Terraform vulnerability
            ↓
        Ground truth
            ↓
   ┌────────┼────────┐
   ↓        ↓        ↓
 KICS     Trivy   Checkov
   └────────┼────────┘
            ↓
      Compare results
            ↓
       Calculate metrics
            ↓
    Analyse complementarity
            ↓
   Combine scanner coverage
            ↓
 Cross-resource correlation
```

This provides a simple technical foundation for the broader research question:

> **Can a multi-layer Terraform security validation approach improve detection coverage compared with relying on a single IaC security scanner?**