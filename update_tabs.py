import sys
sys.path.insert(0, '/home/parker_bailey/frappe/my-bench/apps/frappe')
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

frappe.init(site='site1.local', sites_path='/home/parker_bailey/frappe/my-bench/sites')
frappe.connect()

try:
    frappe.conf.developer_mode = 1
    
    # Check if custom_details_tab is already a standard field
    doc = frappe.get_doc("DocType", "Master Project")
    details_field = next((f for f in doc.fields if f.fieldname == 'custom_details_tab'), None)
    
    if not details_field:
        doc.append('fields', {
            'fieldname': 'custom_details_tab',
            'label': 'Details',
            'fieldtype': 'Tab Break',
            'insert_after': ''
        })
    
    # Set insert_after for all fields that should be under Details
    for f in doc.fields:
        if f.fieldname == 'custom_details_tab':
            f.insert_after = ''
        elif f.fieldname in ['title', 'description', 'projects_html', 'tasks_html']:
            f.insert_after = 'custom_details_tab'
            
    doc.save()
    frappe.db.commit()
    print('Success updating standard fields')
except Exception as e:
    print(f"Error: {e}")
finally:
    frappe.destroy()
