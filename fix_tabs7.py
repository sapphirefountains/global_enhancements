import sys
sys.path.insert(0, '/home/parker_bailey/frappe/my-bench/apps/frappe')
import frappe

frappe.init(site='site1.local', sites_path='/home/parker_bailey/frappe/my-bench/sites')
frappe.connect()

try:
    frappe.conf.developer_mode = 1
    
    doc = frappe.get_doc("DocType", "Master Project")
    
    doc.append('fields', {
        'fieldname': 'custom_details_tab',
        'label': 'Details',
        'fieldtype': 'Tab Break'
    })
    
    # reorder
    fields = doc.fields
    details = fields.pop()
    fields.insert(0, details)
    doc.fields = fields
    
    doc.save()
    frappe.db.commit()
    print('Added Details tab as first field')
except Exception as e:
    print(f"Error: {e}")
finally:
    frappe.destroy()
