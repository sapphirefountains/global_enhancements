import sys
sys.path.insert(0, '/home/parker_bailey/frappe/my-bench/apps/frappe')
import frappe

frappe.init(site='site1.local', sites_path='/home/parker_bailey/frappe/my-bench/sites')
frappe.connect()

try:
    frappe.conf.developer_mode = 1
    doc = frappe.get_doc("DocType", "Master Project")
    
    # Remove all custom_details_tab fields
    doc.fields = [f for f in doc.fields if f.fieldname != 'custom_details_tab']
    
    # Add properly as a child row
    doc.append('fields', {
        'fieldname': 'custom_details_tab',
        'label': 'Details',
        'fieldtype': 'Tab Break',
        'insert_after': ''
    })
    
    # Reorder
    new_fields = []
    details_tab = doc.fields[-1]
    new_fields.append(details_tab)
    
    for f in doc.fields[:-1]:
        new_fields.append(f)
        
    doc.fields = new_fields
    
    doc.save()
    frappe.db.commit()
    print('Fixed Master Project standard fields')
except Exception as e:
    print(f"Error: {e}")
finally:
    frappe.destroy()
