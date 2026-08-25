import os
import re

canonical_metrics = {
    "OOF PR-AUC": "0.9180",
    "OOF 5-Fold PR-AUC": "0.9131 ± 0.0458",
    "OOF Precision @ 0.9899": "1.0000",
    "OOF Recall @ 0.9899": "0.5926",
    "OOF F1 @ 0.9899": "0.7442",
    "Hyperparameter Search Champion PR-AUC": "0.8833 ± 0.0365",
    "Historical CV Benchmark PR-AUC": "0.8807 ± 0.0403",
    "In-Sample Full-Dataset Specificity": "0.99989",
    "In-Sample Full-Dataset Sensitivity": "0.67901",
    "10% Null Stress Test PR-AUC": "0.8383"
}

# Number patterns to flag
pattern = re.compile(r'\b0\.\d{4,5}\b')

canonical_numbers = {"0.9180", "0.9131", "0.0458", "1.0000", "0.5926", "0.7442", "0.8833", "0.0365", "0.8807", "0.0403", "0.9899", "0.8383", "0.99989", "0.67901"}

mismatches = []

for root, dirs, files in os.walk('.'):
    if any(p in root for p in ['.git', 'node_modules', '.next', 'scratch', 'venv']):
        continue
    for f in files:
        if not (f.endswith('.md') or f.endswith('.py') or f.endswith('.json')):
            continue
        fp = os.path.join(root, f)
        try:
            with open(fp, encoding='utf-8', errors='ignore') as file_obj:
                content = file_obj.read()
                matches = pattern.findall(content)
                for num in set(matches):
                    if num not in canonical_numbers and not num.startswith("0.000"):
                        # Check context
                        for line_no, line in enumerate(content.splitlines(), 1):
                            if num in line:
                                mismatches.append((fp, line_no, num, line.strip()[:120]))
        except Exception as e:
            pass

print(f"==========================================")
print(f"REPOS-WIDE METRIC MISMATCH AUDIT")
print(f"==========================================")
print(f"Total metric mismatches flagged: {len(mismatches)}\n")
for fp, line_no, num, line in mismatches:
    clean_line = line.encode('ascii', 'ignore').decode()
    print(f"[{fp}:L{line_no}] Number '{num}' -> {clean_line}")
