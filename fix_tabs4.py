import json

file_path = '/home/parker_bailey/frappe/my-bench/apps/project_enhancements/project_enhancements/project_enhancements/doctype/master_project/master_project.json'

with open(file_path, 'r') as f:
    data = json.load(f)

# The fields are basically ordered by the 'fields' list in the json
fields = data.get('fields', [])

# Remove existing custom_details_tab if any
fields = [f for f in fields if f.get('fieldname') != 'custom_details_tab']

# Insert Details Tab at the very beginning
details_tab = {
    "fieldname": "custom_details_tab",
    "fieldtype": "Tab Break",
    "label": "Details"
}
fields.insert(0, details_tab)

data['fields'] = fields

# Also update field_order
field_order = data.get('field_order', [])
if 'custom_details_tab' in field_order:
    field_order.remove('custom_details_tab')
field_order.insert(0, 'custom_details_tab')
data['field_order'] = field_order

with open(file_path, 'w') as f:
    json.dump(data, f, indent=1)

print("JSON updated successfully")
