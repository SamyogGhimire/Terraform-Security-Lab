import csv

ground_truth = {}

with open("experiment/ground_truth.csv") as f:
    for row in csv.DictReader(f):
        ground_truth[row["case_id"]] = row


# Based on the actual scanner results you supplied.
# 1 = target vulnerability detected
# 0 = target vulnerability not detected

detections = {
    "S01": {"KICS": 1, "Trivy": 1, "Checkov": 1},
    "S02": {"KICS": 1, "Trivy": 1, "Checkov": 1},
    "S03": {"KICS": 1, "Trivy": 0, "Checkov": 1},
    "S04": {"KICS": 1, "Trivy": 1, "Checkov": 1},
    "S05": {"KICS": 0, "Trivy": 1, "Checkov": 1},

    "S06": {"KICS": 0, "Trivy": 0, "Checkov": 0},
    "S07": {"KICS": 0, "Trivy": 0, "Checkov": 0},
    "S08": {"KICS": 0, "Trivy": 0, "Checkov": 0},
    "S09": {"KICS": 0, "Trivy": 0, "Checkov": 0},
    "S10": {"KICS": 0, "Trivy": 0, "Checkov": 0},

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


with open("experiment/detection_matrix.csv", "w", newline="") as f:

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

    for case in ground_truth:

        writer.writerow([
            case,
            ground_truth[case]["corpus"],
            ground_truth[case]["target_vulnerability"],
            ground_truth[case]["label"],
            detections[case]["KICS"],
            detections[case]["Trivy"],
            detections[case]["Checkov"]
        ])

print("Detection matrix created:")
print("experiment/detection_matrix.csv")
