import sys
sys.path.insert(0, '/home/parker_bailey/frappe/my-bench/apps/frappe')
import frappe

frappe.init(site='site1.local', sites_path='/home/parker_bailey/frappe/my-bench/sites')
frappe.connect()

try:
    frappe.conf.developer_mode = 1
    
    # Let's add the custom_details_tab back as a DocType field at the start
    doc = frappe.get_doc("DocType", "Master Project")
    
    new_field = frappe._dict({
        'fieldname': 'custom_details_tab',
        'label': 'Details',
        'fieldtype': 'Tab Break',
        'insert_after': ''
    })
    
    # insert at index 0
    doc.fields.insert(0, new_field)
    
    doc.save()
    frappe.db.commit()
    print('Added Details tab as first field')
except Exception as e:
    print(f"Error: {e}")
finally:
    frappe.destroy()
