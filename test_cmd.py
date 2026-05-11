import json; fields = frappe.get_all('DocField', filters={'parent': 'Master Project'}, fields=['fieldname', 'label', 'fieldtype']); print(fields)
