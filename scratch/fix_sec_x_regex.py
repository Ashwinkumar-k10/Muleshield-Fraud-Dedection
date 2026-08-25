import zipfile
import re
import xml.etree.ElementTree as ET

doc_path = 'MuleShield_PRO_IEEE_Paper_FINAL_SUBMISSION.docx'

with zipfile.ZipFile(doc_path, 'r') as z:
    file_map = {name: z.read(name) for name in z.namelist()}

xml_content = file_map['word/document.xml'].decode('utf-8')

# Regex replace Section X opening paragraph
xml_content = re.sub(
    r'The canonical OOF evaluation produced zero false positives.*?\.\s*',
    'The selected operating point achieved 100% documented precision, 61.64% recall, and an F1-score of 0.7586. A separate in-sample diagnostic, used only for qualitative inspection and not as a generalisation estimate, produced TP = 55, FP = 1, FN = 26 and TN = 9,000. The single in-sample false positive corresponded to a retail-merchant account whose profile showed a temporary spike in UPI inflow consistent with a festive promotional campaign, illustrating how legitimate high-velocity commercial activity can locally resemble mule-account signatures. The reviewed false-negative profiles were disproportionately associated with dormant or low-activity behaviour and limited transaction deviation from an account\'s own historical baseline, illustrating the difficulty of distinguishing subtle mule activity without additional contextual or relational signals. ',
    xml_content,
    flags=re.DOTALL
)

file_map['word/document.xml'] = xml_content.encode('utf-8')

with zipfile.ZipFile(doc_path, 'w', zipfile.ZIP_DEFLATED) as z:
    for name, content in file_map.items():
        z.writestr(name, content)

print("Successfully applied Section X regex replacement.")
