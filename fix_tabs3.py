import json

file_path = '/home/parker_bailey/frappe/my-bench/apps/project_enhancements/project_enhancements/project_enhancements/doctype/master_project/master_project.json'

with open(file_path, 'r') as f:
    data = json.load(f)

# Reorder fields list
fields = data['fields']
details_tab = None
for f in fields:
    if f.get('fieldname') == 'custom_details_tab':
        details_tab = f
        break

if details_tab:
    fields.remove(details_tab)
    fields.insert(0, details_tab)

# Reorder field_order list
field_order = data['field_order']
if 'custom_details_tab' in field_order:
    field_order.remove('custom_details_tab')
field_order.insert(0, 'custom_details_tab')

with open(file_path, 'w') as f:
    json.dump(data, f, indent=1)

print("JSON updated.")
