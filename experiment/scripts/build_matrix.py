import csv

ground_truth = {}

with open("experiment/data/ground_truth.csv") as f:
    for row in csv.DictReader(f):
        ground_truth[row["case_id"]] = row


# Target-vulnerability detection determined from the actual
# KICS, Trivy and Checkov scanner findings.
#
# 1 = target vulnerability detected
# 0 = target vulnerability not detected

detections = {

    # Synthetic vulnerable cases
    "S01": {"KICS": 1, "Trivy": 1, "Checkov": 1},
    "S02": {"KICS": 1, "Trivy": 1, "Checkov": 1},
    "S03": {"KICS": 1, "Trivy": 0, "Checkov": 1},
    "S04": {"KICS": 1, "Trivy": 1, "Checkov": 1},
    "S05": {"KICS": 0, "Trivy": 1, "Checkov": 1},
    "S06": {"KICS": 1, "Trivy": 1, "Checkov": 1},
    "S07": {"KICS": 1, "Trivy": 1, "Checkov": 1},
    "S08": {"KICS": 1, "Trivy": 1, "Checkov": 1},
    "S09": {"KICS": 1, "Trivy": 1, "Checkov": 1},
    "S10": {"KICS": 1, "Trivy": 1, "Checkov": 1},

    # Secure baseline cases:
    # A target vulnerability is absent, so a scanner detecting
    # the target vulnerability would constitute a false positive.
    "B01": {"KICS": 0, "Trivy": 0, "Checkov": 0},
    "B02": {"KICS": 0, "Trivy": 0, "Checkov": 0},
    "B03": {"KICS": 0, "Trivy": 0, "Checkov": 0},
    "B04": {"KICS": 0, "Trivy": 0, "Checkov": 0},
    "B05": {"KICS": 0, "Trivy": 0, "Checkov": 0},
    "B06": {"KICS": 0, "Trivy": 0, "Checkov": 0},
    "B07": {"KICS": 0, "Trivy": 0, "Checkov": 0},
    "B08": {"KICS": 0, "Trivy": 0, "Checkov": 0},
    "B09": {"KICS": 0, "Trivy": 0, "Checkov": 0},
    "B10": {"KICS": 0, "Trivy": 0, "Checkov": 0},
}


with open("experiment/results/detection_matrix.csv", "w", newline="") as f:

    writer = csv.writer(f)

    writer.writerow([
        "case_id",
        "corpus",
        "target_vulnerability",
        "ground_truth",
        "KICS",
        "Trivy",
        "Checkov"
    ])

    for case_id, truth in ground_truth.items():

        writer.writerow([
            case_id,
            truth["corpus"],
            truth["target_vulnerability"],
            truth["ground_truth"],
            detections[case_id]["KICS"],
            detections[case_id]["Trivy"],
            detections[case_id]["Checkov"]
        ])

print("Detection matrix created:")
print("experiment/results/detection_matrix.csv")
