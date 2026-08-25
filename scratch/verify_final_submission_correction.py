import zipfile
import re
import xml.etree.ElementTree as ET

doc_path = 'MuleShield_PRO_IEEE_Paper_FINAL_SUBMISSION.docx'

with zipfile.ZipFile(doc_path, 'r') as z:
    xml_content = z.read('word/document.xml')

root = ET.fromstring(xml_content)

def get_text(element):
    texts = [node.text for node in element.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t') if node.text]
    return ''.join(texts).strip()

paragraphs = [get_text(p) for p in root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p') if get_text(p)]
full_text = '\n'.join(paragraphs)

print(f"=== VERIFYING FINAL CORRECTION PASS ON {doc_path} ===")
print("Total Paragraphs:", len(paragraphs))
print("Total Text Length:", len(full_text))

stale_terms = ['0.9180', '0.9131', '59.26', 'production model', 'production-ready model', 'production deployment', 'production boundary']
for term in stale_terms:
    count = full_text.count(term)
    print(f"Count of '{term}': {count}")

print("\n=== ABSTRACT CHECK ===")
print("Abstract Text Excerpt:")
for p in paragraphs[:15]:
    if 'Abstract' in p or 'leakage-controlled' in p:
        clean = p.encode('ascii', 'ignore').decode()
        print('  ', clean)

print("\n=== FIGURE 5 CAPTION CHECK ===")
for p in paragraphs:
    if 'Fig. 5' in p or 'diagnostic confusion matrix' in p:
        clean = p.encode('ascii', 'ignore').decode()
        print('  ', clean)

print("\n=== TABLE VII ROW CHECK ===")
tables = list(root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tbl'))
if len(tables) > 6:
    for row in tables[6].iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tr'):
        cells = [get_text(c) for c in row.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tc')]
        clean_cells = [c.encode('ascii', 'ignore').decode() for c in cells if c]
        if '0.9899' in clean_cells:
            print('  Table VII Selected Row:', ' | '.join(clean_cells))

print("\nVerification Pass: 100% COMPLETE.")
