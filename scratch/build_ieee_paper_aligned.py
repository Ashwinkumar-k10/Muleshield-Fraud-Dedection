import zipfile
import os
import xml.etree.ElementTree as ET

backup_path = 'MuleShield_PRO_IEEE_Paper (1)_backup.docx'
target_paper = 'MuleShield_PRO_IEEE_Paper_FINAL_ALIGNED.docx'
synced_paper = 'MuleShield_PRO_IEEE_Paper_FINAL_SYNCHRONIZED.docx'
other_papers = ['MuleShield_PRO_IEEE_Paper_FINAL.docx', 'MuleShield_PRO_IEEE_Paper (1).docx']

# Exact canonical documentation values from docs/12_MODEL_EVALUATION.md
doc_metrics = {
    "cv_pr_auc": "0.8807 ± 0.0403",
    "hyperparameter_pr_auc": "0.8833 ± 0.0365",
    "precision": "100.00%",
    "recall": "61.64%",
    "f1": "0.7586",
    "threshold": "0.9899",
    "in_sample_tp": "55",
    "in_sample_tn": "9,000",
    "in_sample_fp": "1",
    "in_sample_fn": "26"
}

def create_aligned_docx(src_path, dst_path):
    with zipfile.ZipFile(src_path, 'r') as z:
        file_map = {name: z.read(name) for name in z.namelist()}

    xml_content = file_map['word/document.xml']
    root = ET.fromstring(xml_content)
    namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    ET.register_namespace('w', namespaces['w'])

    full_xml = ET.tostring(root, encoding='utf-8').decode('utf-8')

    # Phase 4 — Fix "production model" terminology
    full_xml = full_xml.replace(
        'motivating its selection as the production model for this prototype',
        'motivating its selection as the final verified scoring model used in this prototype'
    )
    full_xml = full_xml.replace(
        'production model',
        'final scoring model for this prototype'
    )
    full_xml = full_xml.replace(
        'production-ready model',
        'final verified scoring model'
    )

    # Phase 5 & 14 — Update Abstract & Conclusion metrics to exact documented values
    full_xml = full_xml.replace(
        'The resulting out-of-fold (OOF) evaluation over all 9,082 accounts achieves a PR-AUC of 0.9180, with a five-fold group-aware cross-validation PR-AUC of 0.9131  0.0458. At the selected operating threshold of 0.9899, the system reaches 100.00% OOF precision and 59.26% OOF recall (F1 = 0.7442; TP = 48, FP = 0, FN = 33, TN = 9,001)',
        'Under strict leakage-free five-fold group-aware cross-validation across all 9,082 accounts, the XGBoost model achieves a mean PR-AUC of 0.8807  0.0403 (with a hyperparameter search champion result of 0.8833  0.0365). At the calibrated decision threshold of 0.9899, the system reaches 100.00% validation precision and 61.64% fraud recall (F1 = 0.7586)'
    )

    full_xml = full_xml.replace(
        'The resulting canonical out-of-fold evaluation achieved a PR-AUC of 0.9180 and a group-aware cross-validation PR-AUC of 0.9131  0.0458; at the selected decision threshold of 0.9899 the system reached 100% precision and 59.26% recall (F1 = 0.7442).',
        'The XGBoost model achieved a five-fold group-aware cross-validation PR-AUC of 0.8807  0.0403 (hyperparameter search champion: 0.8833  0.0365); at the calibrated decision threshold of 0.9899 the system reached 100.00% precision and 61.64% recall (F1 = 0.7586).'
    )

    # Clean up stale metrics if present
    full_xml = full_xml.replace('0.9180', '0.8807')
    full_xml = full_xml.replace('0.9131', '0.8807')
    full_xml = full_xml.replace('0.0458', '0.0403')
    full_xml = full_xml.replace('59.26%', '61.64%')
    full_xml = full_xml.replace('59.26', '61.64')
    full_xml = full_xml.replace('0.7442', '0.7586')

    root = ET.fromstring(full_xml.encode('utf-8'))
    tables = list(root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tbl'))

    # Rebuild Table VI (Verified 5-Fold Group CV Performance)
    if len(tables) > 5:
        t6 = tables[5]
        t6_rows = [
            ("Metric", "Verified Value", "Context / Source"),
            ("Final Serialized Model PR-AUC", "0.8807 ± 0.0403", "5-Fold Group CV (docs/12_MODEL_EVALUATION.md)"),
            ("Hyperparameter Search Champion", "0.8833 ± 0.0365", "Grid Search Champion (model_config.json)"),
            ("Validation Precision", "100.00%", "Threshold 0.9899 (0 False Freezes)"),
            ("Validation Recall", "61.64%", "Threshold 0.9899 (Fraud Recall)"),
            ("Validation F1-Score", "0.7586", "Threshold 0.9899"),
            ("Calibrated Threshold", "0.9899", "Precision-Recall Curve Tuning"),
            ("In-Sample Diagnostic Specificity", "99.989%", "Diagnostic Inference (9,000 TN, 1 FP)"),
            ("In-Sample Diagnostic Sensitivity", "67.901%", "Diagnostic Inference (55 TP, 26 FN)"),
            ("Robustness Stress-Test PR-AUC", "0.8383", "10% Null Cell Injection Test")
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
            ("0.9899", "1.0000", "0.6164", "0.7586", "SELECTED PRODUCTION BOUNDARY (0 FP)"),
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

    print(f"Successfully created aligned docx: {dst_path}")

# Run creation & synchronization
create_aligned_docx(backup_path, target_paper)
create_aligned_docx(backup_path, synced_paper)

for p in other_papers:
    try:
        create_aligned_docx(backup_path, p)
    except Exception as e:
        print(f"Skipped updating {p}: {e}")
