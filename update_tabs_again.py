import sys
sys.path.insert(0, '/home/parker_bailey/frappe/my-bench/apps/frappe')
import frappe

frappe.init(site='site1.local', sites_path='/home/parker_bailey/frappe/my-bench/sites')
frappe.connect()

try:
    frappe.conf.developer_mode = 1
    
    # Let's verify Custom Fields
    cfs = frappe.get_all('Custom Field', filters={'dt': 'Master Project'}, fields=['name', 'fieldname', 'insert_after'])
    for cf in cfs:
        if cf.fieldname == 'custom_details_tab':
            # Found it as a Custom Field, delete it
            frappe.delete_doc('Custom Field', cf.name)
            
    frappe.db.commit()
    print('Cleaned up Custom Fields')
except Exception as e:
    print(f"Error: {e}")
finally:
    frappe.destroy()
