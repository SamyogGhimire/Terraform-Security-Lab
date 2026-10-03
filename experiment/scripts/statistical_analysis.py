#!/usr/bin/env python3
"""
Statistical rigor for the controlled benchmark (20 cases: S01-S10, B01-B10).

The headline accuracy/F1 table in the README is a point estimate over only
20 cases. A single flipped case moves accuracy by 5 points, so any claim
that one tool (or the combined framework) is "better" than another needs:

  1. A bootstrap confidence interval on accuracy, to show how much the
     20-case estimate could plausibly vary.
  2. A paired significance test (McNemar's exact test) between tools, to
     check whether an observed difference in correctness is distinguishable
     from chance given the discordant-pair counts.

Reads the official, hand-verified detection matrix at
experiment/results/detection_matrix.csv (the same source used by
calculate_final_metrics.py for the published metrics table).
"""

import csv
import random
from pathlib import Path
from itertools import combinations

from scipy.stats import binomtest

MATRIX = Path("experiment/results/detection_matrix.csv")
OUTPUT = Path("experiment/generated/statistical_analysis.txt")
TOOLS = ["KICS", "Trivy", "Checkov", "Combined"]
N_BOOTSTRAP = 10000
SEED = 42


def load_rows():
    with MATRIX.open() as f:
        rows = list(csv.DictReader(f))

    for row in rows:
        row["ground_truth"] = int(row["ground_truth"])
        for tool in ["KICS", "Trivy", "Checkov"]:
            row[tool] = int(row[tool])
        row["Combined"] = 1 if any(
            row[t] for t in ["KICS", "Trivy", "Checkov"]
        ) else 0

    return rows


def correctness(rows, tool):
    return [1 if row[tool] == row["ground_truth"] else 0 for row in rows]


def accuracy(correct):
    return sum(correct) / len(correct)


def bootstrap_ci(correct, n_bootstrap=N_BOOTSTRAP, seed=SEED):
    rng = random.Random(seed)
    n = len(correct)
    samples = []

    for _ in range(n_bootstrap):
        resample = [correct[rng.randrange(n)] for _ in range(n)]
        samples.append(sum(resample) / n)

    samples.sort()
    lo = samples[int(0.025 * n_bootstrap)]
    hi = samples[int(0.975 * n_bootstrap) - 1]
    return lo, hi


def mcnemar_exact(correct_a, correct_b):
    # Discordant pairs: A right/B wrong (n10), A wrong/B right (n01).
    n10 = sum(1 for a, b in zip(correct_a, correct_b) if a == 1 and b == 0)
    n01 = sum(1 for a, b in zip(correct_a, correct_b) if a == 0 and b == 1)
    n_discordant = n10 + n01

    if n_discordant == 0:
        return n10, n01, 1.0

    p = binomtest(
        min(n10, n01), n_discordant, 0.5, alternative="two-sided"
    ).pvalue
    return n10, n01, p


def main():
    rows = load_rows()
    n_cases = len(rows)

    correctness_by_tool = {tool: correctness(rows, tool) for tool in TOOLS}

    lines = []
    lines.append("STATISTICAL RIGOR: BOOTSTRAP CI AND MCNEMAR'S TEST")
    lines.append("=" * 70)
    lines.append(f"Controlled corpus size: {n_cases} cases (S01-S10, B01-B10)")
    lines.append(
        f"Bootstrap resamples: {N_BOOTSTRAP} (95% percentile interval)"
    )
    lines.append("")
    lines.append("ACCURACY WITH 95% BOOTSTRAP CONFIDENCE INTERVAL")
    lines.append("-" * 70)

    for tool in TOOLS:
        correct = correctness_by_tool[tool]
        acc = accuracy(correct)
        lo, hi = bootstrap_ci(correct)
        lines.append(
            f"{tool:10} accuracy = {acc*100:6.2f}%  "
            f"95% CI = [{lo*100:5.2f}%, {hi*100:5.2f}%]"
        )

    lines.append("")
    lines.append(
        "Note: with n=20, bootstrap resampling cannot manufacture "
        "information the original sample doesn't have. Wide or "
        "overlapping intervals mean the point-estimate ranking between "
        "tools is not well-resolved at this sample size."
    )
    lines.append("")
    lines.append("PAIRWISE MCNEMAR'S EXACT TEST (correctness vs ground truth)")
    lines.append("-" * 70)
    lines.append(
        "H0: the two tools are equally likely to be correct on cases "
        "where they disagree. n10 = tool A correct & tool B wrong; "
        "n01 = tool A wrong & tool B correct."
    )
    lines.append("")

    for a, b in combinations(TOOLS, 2):
        n10, n01, p = mcnemar_exact(
            correctness_by_tool[a], correctness_by_tool[b]
        )
        sig = "significant (p<0.05)" if p < 0.05 else "not significant"
        lines.append(
            f"{a:10} vs {b:10} n10={n10} n01={n01}  p={p:.4f}  ({sig})"
        )

    lines.append("")
    lines.append(
        "Interpretation: with only 1-2 discordant cases between any pair "
        "of tools, McNemar's test has essentially no power at this sample "
        "size. None of the pairwise differences reported here should be "
        "read as statistically established; they describe this specific "
        "20-case corpus, not a population of Terraform configurations. "
        "A corpus of several hundred independently-sourced cases would be "
        "needed before a significance claim is defensible."
    )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(lines) + "\n")

    print("\n".join(lines))
    print()
    print(f"Written to {OUTPUT}")


if __name__ == "__main__":
    main()
