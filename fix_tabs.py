import sys
sys.path.insert(0, '/home/parker_bailey/frappe/my-bench/apps/frappe')
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

frappe.init(site='site1.local', sites_path='/home/parker_bailey/frappe/my-bench/sites')
frappe.connect()

try:
    frappe.conf.developer_mode = 1
    
    # 1. Create Details tab
    fields = [
        {
            'fieldname': 'custom_details_tab',
            'label': 'Details',
            'fieldtype': 'Tab Break',
            'insert_after': ''
        }
    ]
    create_custom_fields({'Master Project': fields})

    # 2. Update standard fields to be under Details
    doc = frappe.get_doc("DocType", "Master Project")
    
    # We need to find the fields and set insert_after, but since standard fields
    # don't officially use insert_after to order against custom fields, we
    # typically just re-order them in the doc.fields list if we can.
    # However, since standard fields are processed first, and Custom Fields are merged in later,
    # if we want the Custom Field "Details" tab to be first, we need to make it a standard field
    # OR we make all other fields custom.
    # Wait, 'Master Project' IS a custom doctype! We can just modify its doc fields directly.
    
    details_tab = None
    for f in doc.fields:
        if f.fieldname == 'custom_details_tab':
            details_tab = f
            break
            
    if not details_tab:
        doc.append('fields', {
            'fieldname': 'custom_details_tab',
            'label': 'Details',
            'fieldtype': 'Tab Break'
        })
        
    # Re-order so custom_details_tab is first
    new_fields = []
    # Add Details Tab first
    for f in doc.fields:
        if f.fieldname == 'custom_details_tab':
            new_fields.append(f)
            break
    # Add the rest
    for f in doc.fields:
        if f.fieldname != 'custom_details_tab':
            new_fields.append(f)
            
    doc.fields = new_fields
    
    doc.save()
    
    # Move Contacts & Addresses after tasks_html
    frappe.db.set_value('Custom Field', 'Master Project-custom_contacts__addresses', 'insert_after', 'tasks_html')
    
    frappe.db.commit()
    print('Success')
except Exception as e:
    print(f"Error: {e}")
finally:
    frappe.destroy()
