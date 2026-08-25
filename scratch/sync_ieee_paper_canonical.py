import zipfile
import os

target_papers = ['MuleShield_PRO_IEEE_Paper_FINAL.docx', 'MuleShield_PRO_IEEE_Paper (1).docx']

for paper_path in target_papers:
    if not os.path.exists(paper_path):
        continue
    
    with zipfile.ZipFile(paper_path, 'r') as z:
        file_map = {name: z.read(name) for name in z.namelist()}
    
    xml_str = file_map['word/document.xml'].decode('utf-8')
    
    # Table 7 exact replacements to align Prec, Rec, F1, and counts with docs/31_CANONICAL_METRICS_TABLE.md
    replacements = [
        # 0.5000 row
        ('0.62', '0.6789'),
        ('0.85', '0.9136'),
        ('0.7168', '0.7789'),
        ('65/14/13/8987', '68/14/13/8987'),
        # 0.7000 row
        ('0.71', '0.8293'),
        ('0.80', '0.8395'),
        ('0.7523', '0.8344'),
        # 0.9000 row
        ('0.85', '0.9275'),
        ('0.75', '0.7901'),
        ('0.7970', '0.8533'),
        # 0.9500 row
        ('0.93', '0.9846'),
        ('0.70', '0.7901'),
        ('0.7986', '0.8767'),
        # 0.9700 row
        ('0.97', '1.0000'),
        ('0.66', '0.7531'),
        ('0.7857', '0.8592'),
        # 0.9800 row
        ('0.99', '1.0000'),
        ('0.63', '0.6667'),
        ('0.7699', '0.8000'),
        # 0.9850 row
        ('1.00', '1.0000'),
        ('0.61', '0.6420'),
        ('0.7578', '0.7820'),
        # 0.9900 row
        ('0.55', '0.5926'),
        ('0.7097', '0.7442'),
        # 0.9950 row
        ('0.42', '0.5679'),
        ('0.5915', '0.7244')
    ]
    
    for old_txt, new_txt in replacements:
        xml_str = xml_str.replace(old_txt, new_txt)
        
    file_map['word/document.xml'] = xml_str.encode('utf-8')
    
    with zipfile.ZipFile(paper_path, 'w', zipfile.ZIP_DEFLATED) as z:
        for name, content in file_map.items():
            z.writestr(name, content)
            
    print(f"Synchronized Table 7 in {paper_path} successfully.")
