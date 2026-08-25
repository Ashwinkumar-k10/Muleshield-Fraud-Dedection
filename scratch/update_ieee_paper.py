import zipfile
import os
import xml.etree.ElementTree as ET

doc_path = 'MuleShield_PRO_IEEE_Paper (1).docx'
backup_path = 'MuleShield_PRO_IEEE_Paper (1)_backup.docx'

if not os.path.exists(backup_path):
    with open(doc_path, 'rb') as src, open(backup_path, 'wb') as dst:
        dst.write(src.read())

print("Created backup of IEEE paper docx.")

# Read zip contents
with zipfile.ZipFile(doc_path, 'r') as z:
    file_map = {name: z.read(name) for name in z.namelist()}

xml_str = file_map['word/document.xml'].decode('utf-8')

# 1. Update Near-duplicate wording
xml_str = xml_str.replace(
    'groups 3,112 near-duplicate profiles into 6,118 similarity clusters',
    'identified 3,112 profiles involved in near-duplicate relationships, producing 6,118 connected similarity components'
)

xml_str = xml_str.replace(
    'A cosine-similarity screen with a threshold above 0.99 identified 3,112 such profiles, which were consolidated into 6,118 similarity groups.',
    'A cosine-similarity screen identified 3,112 profiles involved in near-duplicate relationships; grouping across the full dataset produced 6,118 connected components.'
)

# 2. Fix Production Model Language
xml_str = xml_str.replace(
    'motivating its selection as the production model for this prototype',
    'motivating its selection as the final scoring model for this prototype'
)

# 3. Synchronize Table VII entries
table_replacements = [
    ('69/42/12/8959', '74/35/7/8966'),
    ('27/16/8974', '14/13/8987'),
    ('11/20/8990', '5/17/8996'),
    ('57/4/24/8997', '64/1/17/9000'),
    ('53/2/28/8999', '61/0/20/9001'),
    ('51/1/30/9000', '54/0/27/9001'),
    ('49/0/32/9001', '52/0/29/9001'),
    ('45/0/36/9001', '48/0/33/9001'),
    ('34/0/47/9001', '46/0/35/9001')
]

for old_val, new_val in table_replacements:
    xml_str = xml_str.replace(old_val, new_val)

file_map['word/document.xml'] = xml_str.encode('utf-8')

# Write back zip
with zipfile.ZipFile(doc_path, 'w', zipfile.ZIP_DEFLATED) as z:
    for name, content in file_map.items():
        z.writestr(name, content)

print("Updated MuleShield_PRO_IEEE_Paper (1).docx successfully.")
