import pandas as pd
import xml.etree.ElementTree as ET

print("=== ro-inst.xlsx ===")
df = pd.read_excel('eduroam-kr-data/ro-inst.xlsx')
print(df.columns)
print(df.head(3))

print("\n=== institution.xml ===")
tree = ET.parse('eduroam-kr-data/institution.xml')
root = tree.getroot()
for inst in root.findall('institution')[:2]:
    print("inst_realm:", inst.findtext('inst_realm'))
    print("type:", inst.findtext('type'))
    org_kr = inst.find('org_name[@lang="kr"]')
    print("org_kr:", org_kr.text if org_kr is not None else None)

print("\n=== realm.xml ===")
tree2 = ET.parse('eduroam-kr-data/realm.xml')
root2 = tree2.getroot()
for realm in root2.findall('realm')[:2]:
    org_kr = realm.find('org_name[@lang="kr"]')
    print("org_kr:", org_kr.text if org_kr is not None else None)
    print("country:", realm.findtext('country'))
