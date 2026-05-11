import sys
sys.path.insert(0, '/home/parker_bailey/frappe/my-bench/apps/frappe')
import frappe

frappe.init(site='site1.local', sites_path='/home/parker_bailey/frappe/my-bench/sites')
frappe.connect()

try:
    frappe.conf.developer_mode = 1
    doc = frappe.get_doc("DocType", "Master Project")
    
    # Check if there's any other "custom_details_tab" hiding in Custom Fields that might override our standard one
    cfs = frappe.get_all('Custom Field', filters={'dt': 'Master Project', 'fieldname': 'custom_details_tab'})
    if cfs:
        for cf in cfs:
            frappe.delete_doc('Custom Field', cf.name)
        frappe.db.commit()
        print("Deleted conflicting custom fields")
    else:
        print("No conflicting custom fields")
except Exception as e:
    print(f"Error: {e}")
finally:
    frappe.destroy()
