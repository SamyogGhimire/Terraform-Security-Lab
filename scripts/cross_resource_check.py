#!/usr/bin/env python3
from pathlib import Path
import re
root = Path(__file__).resolve().parents[1] / "cases"
passrole=[]; runinstances=[]
for p in root.rglob("*.tf"):
    t=p.read_text(errors="ignore")
    if re.search(r'iam:PassRole', t): passrole.append(p)
    if re.search(r'ec2:RunInstances', t): runinstances.append(p)
print("CUSTOM CROSS-RESOURCE IAM CHECK")
print("="*40)
print("PassRole files:", [str(p.relative_to(root)) for p in passrole] or "none")
print("RunInstances files:", [str(p.relative_to(root)) for p in runinstances] or "none")
if passrole and runinstances:
    print("RESULT: POTENTIAL CROSS-RESOURCE PRIVILEGE PATH")
else:
    print("RESULT: No PassRole + RunInstances combination detected.")
