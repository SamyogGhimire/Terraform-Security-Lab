from pathlib import Path
from datetime import datetime
import html

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"

def read_file(filename):
    path = RESULTS / filename
    if path.exists():
        return path.read_text(errors="ignore")
    return "Not available"

custom = read_file("custom-iam.txt")
checkov = read_file("checkov.json")
trivy = read_file("trivy.json")

report = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Terraform Security Validation Report</title>

    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 40px;
            background: #f5f7fa;
        }}

        h1 {{
            margin-bottom: 5px;
        }}

        .card {{
            background: white;
            padding: 20px;
            margin: 20px 0;
            border-radius: 10px;
            border: 1px solid #ddd;
        }}

        pre {{
            background: #111827;
            color: #e5e7eb;
            padding: 15px;
            border-radius: 8px;
            overflow-x: auto;
        }}

        .success {{
            padding: 12px;
            background: #dcfce7;
            border-radius: 6px;
        }}
    </style>
</head>

<body>

<h1>Terraform Security Validation Prototype</h1>

<p>
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
</p>

<div class="card">
    <h2>Validation Pipeline</h2>

    <div class="success">
        Terraform → Checkov → Trivy → Custom IAM Analysis
    </div>
</div>

<div class="card">
    <h2>Custom Cross-Resource IAM Analysis</h2>

    <pre>{html.escape(custom)}</pre>
</div>

<div class="card">
    <h2>Checkov Results</h2>

    <pre>{html.escape(checkov[:15000])}</pre>
</div>

<div class="card">
    <h2>Trivy Results</h2>

    <pre>{html.escape(trivy[:15000])}</pre>
</div>

<div class="card">
    <h2>Research Purpose</h2>

    <p>
    This prototype investigates whether combining conventional IaC
    security scanners with additional cross-resource analysis can
    identify security relationships that may not be detected through
    isolated resource-level analysis.
    </p>
</div>

</body>
</html>
"""

output = RESULTS / "report.html"
output.write_text(report)

print(f"Report written to: {output}")
