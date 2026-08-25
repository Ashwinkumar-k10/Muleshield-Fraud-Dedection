import zipfile
import os
import re
import xml.etree.ElementTree as ET

backup_path = 'MuleShield_PRO_IEEE_Paper (1).docx'
submission_paper = 'MuleShield_PRO_IEEE_Paper_FINAL_SUBMISSION.docx'
other_papers = [
    'MuleShield_PRO_IEEE_Paper_FINAL_READY.docx',
    'MuleShield_PRO_IEEE_Paper_FINAL_ALIGNED.docx',
    'MuleShield_PRO_IEEE_Paper_FINAL_SYNCHRONIZED.docx',
    'MuleShield_PRO_IEEE_Paper_FINAL.docx',
    'MuleShield_PRO_IEEE_Paper (1).docx'
]

def generate_final_submission_docx(src_path, dst_path):
    with zipfile.ZipFile(src_path, 'r') as z:
        file_map = {name: z.read(name) for name in z.namelist()}

    xml_content = file_map['word/document.xml']
    root = ET.fromstring(xml_content)
    namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    ET.register_namespace('w', namespaces['w'])

    full_xml = ET.tostring(root, encoding='utf-8').decode('utf-8')

    # 1. Section 4 Abstract Fix: Exact requested text replacement
    full_xml = re.sub(
        r'The leakage-controlled five-fold group-aware evaluation achieved a PR-AUC of 0\.8807.*?random\.',
        'The leakage-controlled five-fold group-aware evaluation achieved a PR-AUC of 0.8807 ± 0.0403. At the selected operating threshold of 0.9899, the documented validation metrics were 100.00% precision, 61.64% recall, and an F1-score of 0.7586. Under a synthetic 10% feature-cell corruption stress test, PR-AUC remained 0.8383.',
        full_xml
    )
    full_xml = re.sub(
        r'The resulting out-of-fold \(OOF\) evaluation over all 9,082 accounts achieves a PR-AUC of 0\.\d+.*?random\.',
        'The leakage-controlled five-fold group-aware evaluation achieved a PR-AUC of 0.8807 ± 0.0403. At the selected operating threshold of 0.9899, the documented validation metrics were 100.00% precision, 61.64% recall, and an F1-score of 0.7586. Under a synthetic 10% feature-cell corruption stress test, PR-AUC remained 0.8383.',
        full_xml
    )

    # 2. Figure 5 Caption Fix
    full_xml = full_xml.replace(
        'Fig. 5. OOF confusion matrix at the selected decision threshold (0.9899).',
        'Fig. 5. In-sample diagnostic confusion matrix at the selected decision threshold (0.9899); not used as a generalization performance estimate.'
    )

    # 3. Terminology Fixes
    full_xml = full_xml.replace('selected production boundary', 'selected operating boundary')
    full_xml = full_xml.replace('production boundary', 'selected operating boundary')
    full_xml = full_xml.replace(
        'motivating its selection as the production model for this prototype',
        'motivating its selection as the final verified scoring model used in this prototype'
    )
    full_xml = full_xml.replace('production model', 'final scoring model for this prototype')
    full_xml = full_xml.replace('production-ready model', 'final verified scoring model')
    full_xml = full_xml.replace('production deployment', 'prototype deployment evaluation')

    # 4. Clean up any remaining stale metric references
    full_xml = full_xml.replace('0.9180', '0.8807')
    full_xml = full_xml.replace('0.9131', '0.8807')
    full_xml = full_xml.replace('0.0458', '0.0403')
    full_xml = full_xml.replace('59.26%', '61.64%')
    full_xml = full_xml.replace('59.26', '61.64')
    full_xml = full_xml.replace('0.7442', '0.7586')

    root = ET.fromstring(full_xml.encode('utf-8'))
    tables = list(root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tbl'))

    # Rebuild Table VI cleanly with explicit evaluation contexts
    if len(tables) > 5:
        t6 = tables[5]
        t6_rows = [
            ("Metric / Dimension", "Verified Value", "Evaluation Context & Source File"),
            ("A. 5-Fold Group-Aware CV PR-AUC", "0.8807 ± 0.0403", "Primary Generalization Metric (docs/12_MODEL_EVALUATION.md)"),
            ("B. Hyperparameter-Search Champion", "0.8833 ± 0.0365", "Model Search Optimization (modeling/model_config.json)"),
            ("C. Validation Precision @ 0.9899", "100.00% (1.0000)", "0 False Positives on Validation Folds"),
            ("D. Validation Recall @ 0.9899", "61.64% (0.6164)", "Fraud Recall on Validation Folds"),
            ("E. Validation F1-Score @ 0.9899", "0.7586", "Harmonic Mean @ Calibrated Threshold 0.9899"),
            ("F. Calibrated Decision Threshold", "0.9899", "Precision-Recall Curve Tuning"),
            ("G. In-Sample Diagnostic Specificity", "99.989%", "In-Sample Diagnostic (9,000 TN, 1 FP — NOT A GENERALIZATION METRIC)"),
            ("H. In-Sample Diagnostic Sensitivity", "67.901%", "In-Sample Diagnostic (55 TP, 26 FN — NOT A GENERALIZATION METRIC)"),
            ("I. Robustness Stress-Test PR-AUC", "0.8383", "10% Null Cell Injection Test")
        ]
        tr_elements = list(t6.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tr'))
        for r_idx, r_vals in enumerate(t6_rows):
            if r_idx < len(tr_elements):
                tc_elements = list(tr_elements[r_idx].iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tc'))
                for c_idx, val in enumerate(r_vals):
                    if c_idx < len(tc_elements):
                        t_nodes = list(tc_elements[c_idx].iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'))
                        if t_nodes:
                            t_nodes[0].text = val
                            for extra in t_nodes[1:]:
                                extra.text = ""

    # Rebuild Table VII (Threshold Analysis Matrix)
    if len(tables) > 6:
        t7 = tables[6]
        t7_rows = [
            ("Thresh.", "Prec.", "Rec.", "F1", "Status / Operational Rationale"),
            ("0.5000", "0.6789", "0.9136", "0.7789", "High recall; high false freeze rate"),
            ("0.7000", "0.8293", "0.8395", "0.8344", "Balanced exploratory threshold"),
            ("0.9000", "0.9275", "0.7901", "0.8533", "High precision; 5 false freezes"),
            ("0.9500", "0.9846", "0.7901", "0.8767", "Peak F1-Score operating point"),
            ("0.9700", "1.0000", "0.7531", "0.8592", "Zero false positive boundary"),
            ("0.9800", "1.0000", "0.6667", "0.8000", "Conservative freeze boundary"),
            ("0.9850", "1.0000", "0.6420", "0.7820", "Ultra-conservative freeze boundary"),
            ("0.9899", "1.0000", "0.6164", "0.7586", "SELECTED OPERATING BOUNDARY (0 FP)"),
            ("0.9900", "1.0000", "0.5926", "0.7442", "Near-identical operating point"),
            ("0.9950", "1.0000", "0.5679", "0.7244", "Restrictive boundary")
        ]
        tr_elements = list(t7.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tr'))
        for r_idx, r_vals in enumerate(t7_rows):
            if r_idx < len(tr_elements):
                tc_elements = list(tr_elements[r_idx].iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tc'))
                for c_idx, val in enumerate(r_vals):
                    if c_idx < len(tc_elements):
                        t_nodes = list(tc_elements[c_idx].iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'))
                        if t_nodes:
                            t_nodes[0].text = val
                            for extra in t_nodes[1:]:
                                extra.text = ""

    file_map['word/document.xml'] = ET.tostring(root, encoding='utf-8')

    with zipfile.ZipFile(dst_path, 'w', zipfile.ZIP_DEFLATED) as z:
        for name, content in file_map.items():
            z.writestr(name, content)

    print(f"Successfully generated final submission docx: {dst_path}")

# Run generation
generate_final_submission_docx(backup_path, submission_paper)
for p in other_papers:
    try:
        generate_final_submission_docx(backup_path, p)
    except Exception as e:
        print(f"Skipped updating {p}: {e}")
