import zipfile
import re
import xml.etree.ElementTree as ET

doc_path = 'MuleShield_PRO_IEEE_Paper_FINAL_SUBMISSION.docx'

with zipfile.ZipFile(doc_path, 'r') as z:
    file_map = {name: z.read(name) for name in z.namelist()}

xml_content = file_map['word/document.xml'].decode('utf-8')

# Ensure exact text below Table VII
old_sentence = 'The 0.9899 row corresponds to the selected documented operating metrics. The surrounding rows are shown only to illustrate the precision-recall trade-off and are not treated as independently audited canonical operating points.'
new_sentence = 'The 0.9899 row represents the selected documented operating point. The surrounding rows illustrate the precision-recall trade-off and are not treated as independently audited operating points.'

xml_content = xml_content.replace(old_sentence, new_sentence)
if new_sentence not in xml_content:
    xml_content = re.sub(
        r'0\.7244\s*\|\s*Restrictive boundary</w:t>.*?</w:tr>\s*</w:tbl>\s*<w:p.*?>',
        f'0.7244 | Restrictive boundary</w:t></w:tc></w:tr></w:tbl><w:p><w:r><w:t>{new_sentence}</w:t></w:r></w:p>',
        xml_content,
        flags=re.DOTALL
    )

# Section X opening sentence exact check
sec_x_exact = 'The selected operating point achieved the documented validation metrics of 100% precision, 61.64% recall, and an F1-score of 0.7586. A separate in-sample diagnostic, used only for qualitative error inspection and not as a generalisation estimate, produced FP = 1 and FN = 26. The single in-sample false positive corresponded to a retail-merchant account whose profile showed a temporary spike in UPI inflow consistent with a festive promotional campaign, illustrating how legitimate high-velocity commercial activity can locally resemble mule-account signatures. The reviewed false-negative profiles were disproportionately associated with dormant or low-activity behaviour and limited transaction deviation from an account\'s own historical baseline, illustrating the difficulty of distinguishing subtle mule activity without additional contextual or relational signals.'

sec_x_old = 'The selected operating point achieved 100% documented precision, 61.64% recall, and an F1-score of 0.7586. A separate in-sample diagnostic, used only for qualitative inspection and not as a generalisation estimate, produced TP = 55, FP = 1, FN = 26 and TN = 9,000. The single in-sample false positive corresponded to a retail-merchant account whose profile showed a temporary spike in UPI inflow consistent with a festive promotional campaign, illustrating how legitimate high-velocity commercial activity can locally resemble mule-account signatures. The reviewed false-negative profiles were disproportionately associated with dormant or low-activity behaviour and limited transaction deviation from an account\'s own historical baseline, illustrating the difficulty of distinguishing subtle mule activity without additional contextual or relational signals.'

xml_content = xml_content.replace(sec_x_old, sec_x_exact)

file_map['word/document.xml'] = xml_content.encode('utf-8')

with zipfile.ZipFile(doc_path, 'w', zipfile.ZIP_DEFLATED) as z:
    for name, content in file_map.items():
        z.writestr(name, content)

print("Exact final micro-fix applied.")
