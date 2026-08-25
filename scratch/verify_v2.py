import zipfile
import xml.etree.ElementTree as ET

doc_path = 'MuleShield_PRO_IEEE_Paper_FINAL_SUBMISSION_V2.docx'

with zipfile.ZipFile(doc_path, 'r') as z:
    xml_content = z.read('word/document.xml')

root = ET.fromstring(xml_content)

def get_text(element):
    texts = [node.text for node in element.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t') if node.text]
    return ''.join(texts).strip()

paragraphs = [get_text(p) for p in root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p') if get_text(p)]
full_text = '\n'.join(paragraphs)

print("=== VERIFYING FINAL MICRO-FIXES ON V2 ===")
stale_terms = ['0.5926', '0.7442', 'FN = 33', '48/0/33/9001', 'canonical confusion counts', 'SELECTED PRODUCTION BOUNDARY']
for term in stale_terms:
    print(f"Count of '{term}': {full_text.count(term)}")

print("\n=== TABLE VII VERIFICATION ===")
tables = list(root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tbl'))
if len(tables) > 6:
    for row in tables[6].iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tr'):
        cells = [get_text(c) for c in row.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tc')]
        clean_cells = [c.encode('ascii', 'ignore').decode() for c in cells if c]
        print('  ', ' | '.join(clean_cells))

print("\n=== TEXT BELOW TABLE VII ===")
for p in paragraphs:
    if 'represents the selected documented operating point' in p:
        print('  ', p.encode('ascii', 'ignore').decode())

print("\n=== SECTION X OPENING SENTENCE ===")
for p in paragraphs:
    if 'achieved the documented validation metrics of 100% precision' in p:
        print('  ', p.encode('ascii', 'ignore').decode())
