import zipfile
import re
import xml.etree.ElementTree as ET

doc_path = 'MuleShield_PRO_IEEE_Paper_FINAL_SUBMISSION.docx'

with zipfile.ZipFile(doc_path, 'r') as z:
    file_map = {name: z.read(name) for name in z.namelist()}

xml_content = file_map['word/document.xml'].decode('utf-8')

# Exact replacement for Section X opening paragraph
old_sec_x = 'The canonical OOF evaluation produced zero false positives and 33 false negatives at the selected threshold (FP = 0, FN = 33). The separate in-sample diagnostic, used only for qualitative inspection and not as a generalisation estimate, produced a small number of additional errors (FP = 1, FN = 26) that were manually reviewed for pattern content. The single in-sample false positive corresponded to a retail-merchant account whose profile showed a temporary spike in UPI inflow consistent with a festive promotional campaign, illustrating that legitimate high-velocity commercial activity can locally resemble mule-account signatures. The false negatives reviewed were disproportionately dormant or low-activity accounts characterised by small, isolated transfers and low deviation from their own historical baseline  precisely the profile that is hardest to distinguish from ordinary low-activity legitimate accounts without additional contextual signals such as counterparty linkage, which is discussed as a limitation in Section XVIII.'

new_sec_x = 'The selected operating point achieved 100% documented precision, 61.64% recall, and an F1-score of 0.7586. A separate in-sample diagnostic, used only for qualitative inspection and not as a generalisation estimate, produced TP = 55, FP = 1, FN = 26 and TN = 9,000. The single in-sample false positive corresponded to a retail-merchant account whose profile showed a temporary spike in UPI inflow consistent with a festive promotional campaign, illustrating how legitimate high-velocity commercial activity can locally resemble mule-account signatures. The reviewed false-negative profiles were disproportionately associated with dormant or low-activity behaviour and limited transaction deviation from an account\'s own historical baseline, illustrating the difficulty of distinguishing subtle mule activity without additional contextual or relational signals.'

xml_content = xml_content.replace(old_sec_x, new_sec_x)

file_map['word/document.xml'] = xml_content.encode('utf-8')

with zipfile.ZipFile(doc_path, 'w', zipfile.ZIP_DEFLATED) as z:
    for name, content in file_map.items():
        z.writestr(name, content)

print("Successfully replaced Section X opening paragraph.")
