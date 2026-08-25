import zipfile
import os
import xml.etree.ElementTree as ET

table7_canonical_rows = [
    ("Thresh.", "Prec.", "Rec.", "F1", "TP/FP/FN/TN"),
    ("0.5000", "0.6789", "0.9136", "0.7789", "74/35/7/8966"),
    ("0.7000", "0.8293", "0.8395", "0.8344", "68/14/13/8987"),
    ("0.9000", "0.9275", "0.7901", "0.8533", "64/5/17/8996"),
    ("0.9500", "0.9846", "0.7901", "0.8767", "64/1/17/9000"),
    ("0.9700", "1.0000", "0.7531", "0.8592", "61/0/20/9001"),
    ("0.9800", "1.0000", "0.6667", "0.8000", "54/0/27/9001"),
    ("0.9850", "1.0000", "0.6420", "0.7820", "52/0/29/9001"),
    ("0.9899", "1.0000", "0.5926", "0.7442", "48/0/33/9001"),
    ("0.9900", "1.0000", "0.5926", "0.7442", "48/0/33/9001"),
    ("0.9950", "1.0000", "0.5679", "0.7244", "46/0/35/9001")
]

# Restore clean target docx from safety backup
backup_path = 'MuleShield_PRO_IEEE_Paper (1)_backup.docx'
target_papers = ['MuleShield_PRO_IEEE_Paper_FINAL.docx', 'MuleShield_PRO_IEEE_Paper (1).docx']

for paper_path in target_papers:
    # First restore fresh backup
    with open(backup_path, 'rb') as src, open(paper_path, 'wb') as dst:
        dst.write(src.read())

    with zipfile.ZipFile(paper_path, 'r') as z:
        file_map = {name: z.read(name) for name in z.namelist()}

    xml_content = file_map['word/document.xml']
    root = ET.fromstring(xml_content)
    namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    ET.register_namespace('w', namespaces['w'])

    # 1. Update text replacements
    full_xml = ET.tostring(root, encoding='utf-8').decode('utf-8')
    full_xml = full_xml.replace(
        'groups 3,112 near-duplicate profiles into 6,118 similarity clusters',
        'identified 3,112 profiles involved in near-duplicate relationships, producing 6,118 connected similarity components'
    )
    full_xml = full_xml.replace(
        'A cosine-similarity screen with a threshold above 0.99 identified 3,112 such profiles, which were consolidated into 6,118 similarity groups.',
        'A cosine-similarity screen identified 3,112 profiles involved in near-duplicate relationships; grouping across the full dataset produced 6,118 connected components.'
    )
    full_xml = full_xml.replace(
        'motivating its selection as the production model for this prototype',
        'motivating its selection as the final scoring model for this prototype'
    )

    root = ET.fromstring(full_xml.encode('utf-8'))
    tables = list(root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tbl'))
    
    # Table 7 is index 6
    t7 = tables[6]
    tr_elements = list(t7.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tr'))
    
    for row_idx, row_vals in enumerate(table7_canonical_rows):
        if row_idx < len(tr_elements):
            tc_elements = list(tr_elements[row_idx].iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tc'))
            for col_idx, val in enumerate(row_vals):
                if col_idx < len(tc_elements):
                    t_nodes = list(tc_elements[col_idx].iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'))
                    if t_nodes:
                        t_nodes[0].text = val
                        for extra_t in t_nodes[1:]:
                            extra_t.text = ""

    file_map['word/document.xml'] = ET.tostring(root, encoding='utf-8')

    with zipfile.ZipFile(paper_path, 'w', zipfile.ZIP_DEFLATED) as z:
        for name, content in file_map.items():
            z.writestr(name, content)

    print(f"Rebuilt Table 7 in {paper_path} cleanly.")
