import re
import json
import xml.etree.ElementTree as ET

def sort_key(name):
    stripped = re.sub(r'^\([^)]+\)', '', name).strip()
    return stripped if stripped else name

def instid_to_logo(instid):
    return instid.replace('.', '_') + '.png'

def get_text_lang(parent, tag, lang):
    for elem in parent.findall(tag):
        if elem.get('lang') == lang:
            return (elem.text or '').strip()
    return ''

def get_text(parent, tag):
    elem = parent.find(tag)
    return (elem.text or '').strip() if elem is not None else ''

xml_path = 'general/institution.ref.v2.xml'
tree = ET.parse(xml_path)
root = tree.getroot()

institutions_raw = []
for inst in root.findall('institution'):
    instid = get_text(inst, 'instid')
    inst_realm = get_text(inst, 'inst_realm')
    name_ko = get_text_lang(inst, 'inst_name', 'ko') or get_text_lang(inst, 'inst_name', 'en')
    guide = get_text_lang(inst, 'info_URL', 'ko') or get_text_lang(inst, 'info_URL', 'en')

    # Optional <type_kr> element (국립/사립/기타) — not in v2 spec but supported as extension
    type_kr = get_text(inst, 'type_kr')
    if not type_kr:
        type_kr = '기타'

    # <type> element: IdP | SP | IdP+SP
    conn_type = get_text(inst, 'type')

    # Each <location> becomes one campus entry; fall back to single "본교"
    campuses = []
    for loc in inst.findall('location'):
        loc_name = (
            get_text_lang(loc, 'loc_name', 'ko')
            or get_text_lang(loc, 'loc_name', 'en')
            or '본교'
        )
        loc_guide = (
            get_text_lang(loc, 'info_URL', 'ko')
            or get_text_lang(loc, 'info_URL', 'en')
            or guide
        )
        campuses.append({'name': loc_name, 'realm': inst_realm, 'guide': loc_guide})

    if not campuses:
        campuses = [{'name': '본교', 'realm': inst_realm, 'guide': guide}]

    institutions_raw.append({
        'name': name_ko,
        'instid': instid,
        'logo': instid_to_logo(instid),
        'type': type_kr,
        'conn_type': conn_type,
        'campuses': campuses,
    })

institutions_raw.sort(key=lambda x: sort_key(x['name']))

# --- institutions.json ---
institutions_list = []
for idx, inst in enumerate(institutions_raw, 1):
    realms = [c['realm'] for c in inst['campuses']]
    institutions_list.append({
        'id': idx,
        'type': inst['type'],
        'conn_type': inst['conn_type'],
        'name': inst['name'],
        'logo': inst['logo'],
        'campuses': inst['campuses'],
        'rowspan_realm': len(set(realms)) == 1,
    })

with open('_data/institutions.json', 'w', encoding='utf-8') as f:
    json.dump(institutions_list, f, ensure_ascii=False, indent=2)

# --- institutions_pages.json ---
flat_rows = []
serial_no = 1
total_campuses = 0
for inst in institutions_list:
    page_idx = (serial_no - 1) // 15 + 1
    flat_rows.append({
        'serial_no': serial_no,
        'page': page_idx,
        'logo': inst['logo'],
        'univ_name': inst['name'],
        'inst_type': inst['type'],
        'conn_type': inst['conn_type'],
        'guide': inst['campuses'][0]['guide'] if inst['campuses'] else '',
        'realms': [c['realm'] for c in inst['campuses']],
    })
    total_campuses += len(inst['campuses'])
    serial_no += 1

pages_dict = {}
for r in flat_rows:
    p = r['page']
    if p not in pages_dict:
        pages_dict[p] = []
    pages_dict[p].append(r)

pages_list = [{'page': p, 'rows': pages_dict[p]} for p in sorted(pages_dict.keys())]

output_data = {
    'total_campuses': total_campuses,
    'total_institutions': len(institutions_list),
    'pages': pages_list,
    'total_pages': len(pages_list),
}

with open('_data/institutions_pages.json', 'w', encoding='utf-8') as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)

print(f"Generated {len(pages_list)} page(s), {len(institutions_list)} institution(s), {total_campuses} campus(es).")
