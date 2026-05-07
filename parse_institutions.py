import re
import json
import pandas as pd

def sort_key(name):
    # (재), (사) 등 앞에 붙은 법인 표기를 제거하고 정렬
    stripped = re.sub(r'^\([^)]+\)', '', name).strip()
    return stripped if stripped else name

excel_path = 'eduroam-kr-data/ro-inst.xlsx'

df_inst = pd.read_excel(excel_path, sheet_name='inst').fillna('')
df_campus = pd.read_excel(excel_path, sheet_name='campus').fillna('')

# Count campuses per institution for stats
campus_count = {}
for _, row in df_campus.iterrows():
    uname = row['univ_name'].strip()
    campus_count[uname] = campus_count.get(uname, 0) + 1

# Sort institutions by name
institutions = []
for _, row in df_inst.iterrows():
    name = row['univ_name_ko'].strip()
    institutions.append({'raw_row': row, 'name': name})
institutions = sorted(institutions, key=lambda x: sort_key(x['name']))

# One row per institution
flat_rows = []
serial_no = 1
total_campuses = 0

for item in institutions:
    row = item['raw_row']
    name = item['name']

    realms_str = str(row['realm']).strip()
    realms = [r.strip() for r in realms_str.split(',') if r.strip()]
    guide_str = str(row['guide_url']).strip()
    guides = [g.strip() for g in guide_str.split(',') if g.strip()]

    page_idx = (serial_no - 1) // 15 + 1

    flat_rows.append({
        'serial_no': serial_no,
        'page': page_idx,
        'logo': row['logo_url'].strip(),
        'univ_name': name,
        'inst_type': row['univ_type'].strip(),
        'guide': guides[0] if guides else '',
        'realms': realms,
    })

    total_campuses += campus_count.get(name, 1)
    serial_no += 1

# Group by page
pages_dict = {}
for r in flat_rows:
    p = r['page']
    if p not in pages_dict:
        pages_dict[p] = []
    pages_dict[p].append(r)

pages_list = [{'page': p, 'rows': pages_dict[p]} for p in sorted(pages_dict.keys())]

output_data = {
    'total_campuses': total_campuses,
    'total_institutions': len(institutions),
    'pages': pages_list,
    'total_pages': len(pages_list)
}

with open('_data/institutions_pages.json', 'w', encoding='utf-8') as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)

print(f"Successfully generated {len(pages_list)} pages with {len(institutions)} institutions.")
