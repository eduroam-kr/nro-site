import os
import json
import pandas as pd

excel_path = 'eduroam-kr-data/ro-inst.xlsx'

df_inst = pd.read_excel(excel_path, sheet_name='inst').fillna('')
df_campus = pd.read_excel(excel_path, sheet_name='campus').fillna('')

campus_map = {}
for _, row in df_campus.iterrows():
    uname = row['univ_name'].strip()
    cname = row['campus_name'].strip()
    if uname not in campus_map:
        campus_map[uname] = []
    campus_map[uname].append(cname)

# First group by institution and sort
institutions = []
for index, row in df_inst.iterrows():
    name = row['univ_name_ko'].strip()
    institutions.append({
        'raw_row': row,
        'name': name
    })
institutions = sorted(institutions, key=lambda x: x['name'])

# Flatten to page rows
flat_rows = []
serial_no = 1
inst_id_counter = 1

for item in institutions:
    row = item['raw_row']
    name = item['name']
    
    realms_str = str(row['realm']).strip()
    realms = [r.strip() for r in realms_str.split(',') if r.strip()]
    guide_str = str(row['guide_url']).strip()
    guides = [g.strip() for g in guide_str.split(',') if g.strip()]
    
    c_list = campus_map.get(name, [])
    if not c_list:
        c_list = ['본교']
        
    num_campuses = len(c_list)
    num_realms = len(realms)
    rowspan_realm = (num_realms == 1)
    
    for i, cname in enumerate(c_list):
        page_idx = (serial_no - 1) // 15 + 1
        
        if rowspan_realm:
            r_val = realms[0] if realms else ''
            g_val = guides[0] if guides else ''
        else:
            r_val = realms[i] if i < len(realms) else (realms[-1] if realms else '')
            g_val = guides[i] if i < len(guides) else (guides[-1] if guides else '')
            
        # NRO/RO Dummy logic for UI demonstration
        operator_type = "NRO"
        if "교육" in name or "재단" in name or (inst_id_counter % 12 == 0):
            operator_type = "RO"

        flat_rows.append({
            'serial_no': serial_no,
            'page': page_idx,
            'inst_id': inst_id_counter,
            'operator_type': operator_type,
            'inst_type': row['univ_type'].strip(),
            'logo': row['logo_url'].strip(),
            'univ_name': name,
            'campus_name': cname,
            'guide': g_val,
            'realm': r_val,
            'rowspan_realm': rowspan_realm
        })
        serial_no += 1
    inst_id_counter += 1

# Calculate chunk properties
for r in flat_rows:
    p = r['page']
    iid = r['inst_id']
    # find all rows in same page and same inst
    chunk = [x for x in flat_rows if x['page'] == p and x['inst_id'] == iid]
    r['chunk_size'] = len(chunk)
    r['is_first_in_chunk'] = (r['serial_no'] == chunk[0]['serial_no'])

# We can output grouped by page so Liquid template is even simpler
# _data/pages.json -> [ { page: 1, rows: [...] }, { page: 2, rows: [...] } ]
pages_dict = {}
for r in flat_rows:
    p = r['page']
    if p not in pages_dict:
        pages_dict[p] = []
    pages_dict[p].append(r)

pages_list = []
for p in sorted(pages_dict.keys()):
    pages_list.append({
        'page': p,
        'rows': pages_dict[p]
    })

output_data = {
    'total_campuses': serial_no - 1,
    'total_institutions': len(institutions),
    'pages': pages_list,
    'total_pages': len(pages_list)
}

with open('_data/institutions_pages.json', 'w', encoding='utf-8') as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)

print(f"Successfully generated {len(pages_list)} pages of data.")
