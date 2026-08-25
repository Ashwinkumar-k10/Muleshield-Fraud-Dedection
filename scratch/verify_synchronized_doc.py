import zipfile
import re
import xml.etree.ElementTree as ET

doc_path = 'MuleShield_PRO_IEEE_Paper_FINAL_SYNCHRONIZED.docx'

with zipfile.ZipFile(doc_path, 'r') as z:
    xml_content = z.read('word/document.xml')

root = ET.fromstring(xml_content)

def get_text(element):
    texts = [node.text for node in element.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t') if node.text]
    return ''.join(texts).strip()

paragraphs = []
for p in root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
    txt = get_text(p)
    if txt:
        paragraphs.append(txt)

full_text = '\n'.join(paragraphs)

print(f"=== VERIFYING {doc_path} ===")
print("Total Paragraphs:", len(paragraphs))
print("Total Text Length:", len(full_text))

stale_metrics = ['0.9180', '0.9131', '59.26%', '0.7442', '48/0/33/9001']
for metric in stale_metrics:
    count = full_text.count(metric)
    print(f"Count of '{metric}': {count}")

print("\n=== KEY METRICS IN ABSTRACT & CONCLUSION ===")
for p in paragraphs[:15] + paragraphs[-15:]:
    if any(k in p for k in ['PR-AUC', 'Precision', 'Recall', 'F1', '0.8807', '0.8833', '0.9899', '61.64%']):
        clean = p.encode('ascii', 'ignore').decode()
        print('  ', clean[:120])

print("\n=== TABLES IN SYNCHRONIZED DOCX ===")
tables = list(root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tbl'))
for idx in [3, 4, 5, 6]:
    if idx < len(tables):
        print(f"\n--- Table {idx+1} ---")
        for row in tables[idx].iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tr'):
            cells = [get_text(c) for c in row.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tc')]
            clean_cells = [c.encode('ascii', 'ignore').decode() for c in cells if c]
            if clean_cells:
                print(' | '.join(clean_cells))
