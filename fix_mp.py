import sys
import json
sys.path.insert(0, '/home/parker_bailey/frappe/my-bench/apps/frappe')
import frappe

frappe.init(site='site1.local', sites_path='/home/parker_bailey/frappe/my-bench/sites')
frappe.connect()

try:
    frappe.conf.developer_mode = 1
    doc = frappe.get_doc("DocType", "Master Project")
    
    # Remove all custom_details_tab fields
    doc.fields = [f for f in doc.fields if f.fieldname != 'custom_details_tab']
    
    # Prepend custom_details_tab
    new_field = frappe._dict({
        'fieldname': 'custom_details_tab',
        'label': 'Details',
        'fieldtype': 'Tab Break',
        'insert_after': ''
    })
    doc.fields.insert(0, new_field)
    
    doc.save()
    frappe.db.commit()
    print('Fixed Master Project standard fields')
except Exception as e:
    print(f"Error: {e}")
finally:
    frappe.destroy()
