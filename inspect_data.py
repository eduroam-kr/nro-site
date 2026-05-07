import xml.etree.ElementTree as ET

print("=== general/institution.ref.v2.xml ===")
tree = ET.parse('general/institution.ref.v2.xml')
root = tree.getroot()
for inst in root.findall('institution')[:3]:
    print("instid:", inst.findtext('instid'))
    print("inst_realm:", inst.findtext('inst_realm'))
    name_ko = next(
        (e.text for e in inst.findall('inst_name') if e.get('lang') == 'ko'), None
    )
    print("inst_name_ko:", name_ko)

print("\n=== general/realm.xml ===")
tree2 = ET.parse('general/realm.xml')
root2 = tree2.getroot()
for realm in root2.findall('realm')[:2]:
    name_en = next(
        (e.text for e in realm.findall('inst_name') if e.get('lang') == 'en'), None
    )
    print("inst_name_en:", name_en)
    print("country:", realm.findtext('country'))
