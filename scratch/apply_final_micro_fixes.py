import zipfile
import re
import xml.etree.ElementTree as ET

doc_path = 'MuleShield_PRO_IEEE_Paper_FINAL_SUBMISSION.docx'

with zipfile.ZipFile(doc_path, 'r') as z:
    file_map = {name: z.read(name) for name in z.namelist()}

xml_content = file_map['word/document.xml'].decode('utf-8')

# CHANGE 2: Text below Table VII replacement
old_t7_text = 'The 0.9899 row corresponds to the selected documented operating metrics. The surrounding rows are shown only to illustrate the precision-recall trade-off and are not treated as independently audited canonical operating points.'
new_t7_text = 'The 0.9899 row represents the selected documented operating point. The surrounding rows illustrate the precision-recall trade-off and are not treated as independently audited operating points.'

xml_content = xml_content.replace(old_t7_text, new_t7_text)
xml_content = re.sub(r'Only the 0\.9899 row reproduces the exact canonical OOF confusion counts.*?\.', new_t7_text, xml_content)

# CHANGE 3: Section X opening sentence replacement
old_sec_x_start = 'The canonical OOF evaluation produced zero false positives and 33 false negatives at the selected threshold (FP = 0, FN = 33).'
new_sec_x_start = 'The selected operating point achieved the documented validation metrics of 100% precision, 61.64% recall, and an F1-score of 0.7586. A separate in-sample diagnostic, used only for qualitative error inspection and not as a generalisation estimate, produced FP = 1 and FN = 26.'

xml_content = xml_content.replace(old_sec_x_start, new_sec_x_start)

# CHANGE 4: Terminology check
xml_content = xml_content.replace('SELECTED PRODUCTION BOUNDARY', 'SELECTED OPERATING BOUNDARY')
xml_content = xml_content.replace('production boundary', 'selected operating boundary')

root = ET.fromstring(xml_content.encode('utf-8'))
tables = list(root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tbl'))

# CHANGE 1: Table VII - Ensure 0.9900 row is gone and 0.9899 row is exact
if len(tables) > 6:
    t7 = tables[6]
    t7_rows = [
        ('Thresh.', 'Prec.', 'Rec.', 'F1', 'Status / Operational Rationale'),
        ('0.5000', '0.6789', '0.9136', '0.7789', 'High recall; high false freeze rate'),
        ('0.7000', '0.8293', '0.8395', '0.8344', 'Balanced exploratory threshold'),
        ('0.9000', '0.9275', '0.7901', '0.8533', 'High precision; 5 false freezes'),
        ('0.9500', '0.9846', '0.7901', '0.8767', 'Peak F1-Score operating point'),
        ('0.9700', '1.0000', '0.7531', '0.8592', 'Zero false positive boundary'),
        ('0.9800', '1.0000', '0.6667', '0.8000', 'Conservative freeze boundary'),
        ('0.9850', '1.0000', '0.6420', '0.7820', 'Ultra-conservative freeze boundary'),
        ('0.9899', '1.0000', '0.6164', '0.7586', 'SELECTED OPERATING BOUNDARY (0 FP)'),
        ('0.9950', '1.0000', '0.5679', '0.7244', 'Restrictive boundary')
    ]
    tr_elements = list(t7.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tr'))
    if len(tr_elements) > len(t7_rows):
        t7.remove(tr_elements[9]) # Remove 0.9900 row
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
                            extra.text = ''

file_map['word/document.xml'] = ET.tostring(root, encoding='utf-8')

with zipfile.ZipFile(doc_path, 'w', zipfile.ZIP_DEFLATED) as z:
    for name, content in file_map.items():
        z.writestr(name, content)

print("Successfully applied final 4 micro-fixes to:", doc_path)
