#!/usr/bin/env python3

import json
import csv
from pathlib import Path
from collections import Counter

BASE = Path("dataset/independent/iacsecbench")
RESULTS = Path("results/independent/iacsecbench")
OUTPUT = Path("experiment/generated/independent")

KICS_DIR = RESULTS / "kics"
TRIVY_DIR = RESULTS / "trivy"
CHECKOV_DIR = RESULTS / "checkov"

OUTPUT.mkdir(parents=True, exist_ok=True)


def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"WARNING: Could not read {path}: {e}")
        return {}


def terraform_stats(repo):
    tf_files = list(repo.rglob("*.tf"))

    loc = 0
    resources = 0
    modules = 0

    for tf in tf_files:
        text = tf.read_text(
            encoding="utf-8",
            errors="ignore"
        )

        for line in text.splitlines():
            stripped = line.strip()

            if stripped and not stripped.startswith("#"):
                loc += 1

            if stripped.startswith("resource "):
                resources += 1

            if stripped.startswith("module "):
                modules += 1

    return len(tf_files), loc, resources, modules


# ---------------------------------------------------------
# KICS
# ---------------------------------------------------------

def kics_stats(repo_id):

    path = KICS_DIR / repo_id / "results.json"

    if not path.exists():
        return {
            "findings": 0,
            "severity": Counter(),
            "categories": Counter(),
        }

    data = load_json(path)

    findings = data.get("total_counter", 0)

    severity = Counter()

    for sev, count in data.get(
        "severity_counters", {}
    ).items():

        if count:
            severity[str(sev).upper()] += count

    categories = Counter()

    for query in data.get("queries", []):

        name = query.get(
            "query_name",
            "UNKNOWN"
        )

        count = len(
            query.get("files", [])
        )

        categories[name] += count

    return {
        "findings": findings,
        "severity": severity,
        "categories": categories,
    }


# ---------------------------------------------------------
# TRIVY
# ---------------------------------------------------------

def trivy_stats(repo_id):

    path = TRIVY_DIR / repo_id / "results.json"

    if not path.exists():
        return {
            "findings": 0,
            "severity": Counter(),
            "categories": Counter(),
        }

    data = load_json(path)

    severity = Counter()
    categories = Counter()

    total = 0

    for result in data.get("Results", []):

        findings = result.get(
            "Misconfigurations",
            []
        )

        total += len(findings)

        for finding in findings:

            sev = str(
                finding.get(
                    "Severity",
                    "UNKNOWN"
                )
            ).upper()

            severity[sev] += 1

            title = finding.get(
                "Title",
                "UNKNOWN"
            )

            categories[title] += 1

    return {
        "findings": total,
        "severity": severity,
        "categories": categories,
    }


# ---------------------------------------------------------
# CHECKOV
# ---------------------------------------------------------

def find_checkov_json(repo_id):

    directory = CHECKOV_DIR / repo_id / "results.json"

    if not directory.exists():
        return None

    if directory.is_file():
        return directory

    json_files = list(
        directory.rglob("*.json")
    )

    if not json_files:
        return None

    return json_files[0]


def checkov_stats(repo_id):

    path = find_checkov_json(repo_id)

    if path is None:
        return {
            "findings": 0,
            "severity": Counter(),
            "categories": Counter(),
        }

    data = load_json(path)

    # Checkov may return either:
    # 1. a single dictionary
    # 2. a list of report dictionaries
    if isinstance(data, dict):
        reports = [data]

    elif isinstance(data, list):
        reports = data

    else:
        reports = []

    severity = Counter()
    categories = Counter()

    total = 0

    for report in reports:

        if not isinstance(report, dict):
            continue

        results = report.get("results", {})

        if not isinstance(results, dict):
            continue

        failed = results.get(
            "failed_checks",
            []
        )

        if not isinstance(failed, list):
            continue

        total += len(failed)

        for finding in failed:

            if not isinstance(finding, dict):
                continue

            sev = str(
                finding.get(
                    "severity",
                    "UNKNOWN"
                )
            ).upper()

            severity[sev] += 1

            check_name = finding.get(
                "check_name",
                finding.get(
                    "check_id",
                    "UNKNOWN"
                )
            )

            categories[check_name] += 1

    return {
        "findings": total,
        "severity": severity,
        "categories": categories,
    }


# ---------------------------------------------------------
# MAIN ANALYSIS
# ---------------------------------------------------------

def main():

    repositories = sorted(
        p for p in BASE.iterdir()
        if p.is_dir()
    )

    rows = []

    totals = {
        "KICS": 0,
        "Trivy": 0,
        "Checkov": 0,
    }

    severity_totals = {
        "KICS": Counter(),
        "Trivy": Counter(),
        "Checkov": Counter(),
    }

    category_totals = {
        "KICS": Counter(),
        "Trivy": Counter(),
        "Checkov": Counter(),
    }

    total_files = 0
    total_loc = 0
    total_resources = 0
    total_modules = 0

    for repo in repositories:

        repo_id = repo.name

        tf_files, loc, resources, modules = (
            terraform_stats(repo)
        )

        kics = kics_stats(repo_id)
        trivy = trivy_stats(repo_id)
        checkov = checkov_stats(repo_id)

        scanners = {
            "KICS": kics,
            "Trivy": trivy,
            "Checkov": checkov,
        }

        for scanner, result in scanners.items():

            totals[scanner] += result["findings"]

            severity_totals[
                scanner
            ].update(result["severity"])

            category_totals[
                scanner
            ].update(result["categories"])

        combined = sum(
            result["findings"]
            for result in scanners.values()
        )

        total_files += tf_files
        total_loc += loc
        total_resources += resources
        total_modules += modules

        rows.append({
            "repository": repo_id,
            "terraform_files": tf_files,
            "terraform_loc": loc,
            "terraform_resources": resources,
            "terraform_modules": modules,
            "kics_findings": kics["findings"],
            "trivy_findings": trivy["findings"],
            "checkov_findings": checkov["findings"],
            "combined_raw_findings": combined,
            "findings_per_1000_loc": round(
                combined / loc * 1000,
                3
            ) if loc else 0,
            "findings_per_resource": round(
                combined / resources,
                3
            ) if resources else 0,
        })

    # -----------------------------------------------------
    # Repository metrics
    # -----------------------------------------------------

    repository_file = (
        OUTPUT / "repository_metrics.csv"
    )

    with open(
        repository_file,
        "w",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=rows[0].keys()
        )

        writer.writeheader()
        writer.writerows(rows)

    # -----------------------------------------------------
    # Scanner summary
    # -----------------------------------------------------

    scanner_file = (
        OUTPUT / "scanner_summary.csv"
    )

    scanner_rows = []

    for scanner in [
        "KICS",
        "Trivy",
        "Checkov"
    ]:

        scanner_rows.append({
            "scanner": scanner,
            "total_findings": totals[scanner],
            "repositories_with_findings": sum(
                1
                for row in rows
                if row[
                    scanner.lower() + "_findings"
                ] > 0
            ),
            "average_findings_per_repository": round(
                totals[scanner] / len(rows),
                3
            ),
        })

    with open(
        scanner_file,
        "w",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=scanner_rows[0].keys()
        )

        writer.writeheader()
        writer.writerows(scanner_rows)

    # -----------------------------------------------------
    # Severity
    # -----------------------------------------------------

    severity_file = (
        OUTPUT / "severity_distribution.csv"
    )

    all_severities = sorted(
        set().union(
            *[
                set(counter.keys())
                for counter in severity_totals.values()
            ]
        )
    )

    with open(
        severity_file,
        "w",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.writer(f)

        writer.writerow(
            ["scanner"] + all_severities
        )

        for scanner in [
            "KICS",
            "Trivy",
            "Checkov"
        ]:

            writer.writerow(
                [scanner] +
                [
                    severity_totals[scanner].get(
                        severity,
                        0
                    )
                    for severity in all_severities
                ]
            )

    # -----------------------------------------------------
    # Finding categories
    # -----------------------------------------------------

    category_file = (
        OUTPUT / "finding_categories.csv"
    )

    with open(
        category_file,
        "w",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.writer(f)

        writer.writerow([
            "scanner",
            "finding",
            "count"
        ])

        for scanner in [
            "KICS",
            "Trivy",
            "Checkov"
        ]:

            for finding, count in (
                category_totals[scanner]
                .most_common()
            ):

                writer.writerow([
                    scanner,
                    finding,
                    count
                ])

    # -----------------------------------------------------
    # Summary
    # -----------------------------------------------------

    summary_file = (
        OUTPUT / "dataset_summary.txt"
    )

    combined = sum(totals.values())

    with open(
        summary_file,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            "IaCSecBench Independent Real-World Dataset\n"
        )

        f.write("=" * 55 + "\n\n")

        f.write(
            f"Repositories analysed: "
            f"{len(repositories)}\n"
        )

        f.write(
            f"Terraform files: "
            f"{total_files}\n"
        )

        f.write(
            f"Terraform LOC: "
            f"{total_loc}\n"
        )

        f.write(
            f"Terraform resources: "
            f"{total_resources}\n"
        )

        f.write(
            f"Terraform modules: "
            f"{total_modules}\n\n"
        )

        f.write(
            "Scanner findings\n"
        )

        f.write("-" * 30 + "\n")

        for scanner in [
            "KICS",
            "Trivy",
            "Checkov"
        ]:

            f.write(
                f"{scanner}: "
                f"{totals[scanner]}\n"
            )

        f.write(
            f"Combined raw findings: "
            f"{combined}\n\n"
        )

        if total_loc:

            f.write(
                "Combined findings per 1,000 "
                "Terraform LOC: "
                f"{combined / total_loc * 1000:.3f}\n"
            )

        if total_resources:

            f.write(
                "Combined findings per Terraform "
                "resource: "
                f"{combined / total_resources:.3f}\n"
            )

        f.write(
            "\nSeverity distribution\n"
        )

        f.write("-" * 30 + "\n")

        for scanner in [
            "KICS",
            "Trivy",
            "Checkov"
        ]:

            f.write(
                f"\n{scanner}\n"
            )

            for severity, count in (
                severity_totals[scanner]
                .most_common()
            ):

                f.write(
                    f"  {severity}: {count}\n"
                )

    print()
    print("=" * 55)
    print("IaCSecBench analysis complete")
    print("=" * 55)
    print(f"Repositories: {len(repositories)}")
    print(f"Terraform files: {total_files}")
    print(f"Terraform LOC: {total_loc}")
    print(f"Terraform resources: {total_resources}")
    print()
    print(f"KICS findings: {totals['KICS']}")
    print(f"Trivy findings: {totals['Trivy']}")
    print(f"Checkov findings: {totals['Checkov']}")
    print(f"Combined: {combined}")
    print()
    print(f"Output: {OUTPUT}")
    print("=" * 55)


if __name__ == "__main__":
    main()