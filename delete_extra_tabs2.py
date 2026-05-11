import sys
import json
sys.path.insert(0, '/home/parker_bailey/frappe/my-bench/apps/frappe')
import frappe

frappe.init(site='site1.local', sites_path='/home/parker_bailey/frappe/my-bench/sites')
frappe.connect()

try:
    frappe.conf.developer_mode = 1
    doc = frappe.get_doc("DocType", "Master Project")
    
    # Let's completely nuke custom_details_tab from DocType
    doc.fields = [f for f in doc.fields if f.fieldname != 'custom_details_tab']
    doc.save()
    frappe.db.commit()
    print('Removed custom_details_tab from DocType')
except Exception as e:
    print(f"Error: {e}")
finally:
    frappe.destroy()
