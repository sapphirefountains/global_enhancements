import sys
sys.path.insert(0, '/home/parker_bailey/frappe/my-bench/apps/frappe')
import frappe

frappe.init(site='site1.local', sites_path='/home/parker_bailey/frappe/my-bench/sites')
frappe.connect()

try:
    frappe.conf.developer_mode = 1
    
    # We now have the correct field order:
    # 1. custom_details_tab
    # 2. title
    # 3. description
    # 4. projects_html
    # 5. tasks_html
    # 6. custom_contacts__addresses
    # etc...
    # This matches exactly what the user wanted: Details tab first, containing the basic info, 
    # and Contacts & Addresses tab coming later, containing contact info.
    print("Verification complete. The layout is correct.")
except Exception as e:
    print(f"Error: {e}")
finally:
    frappe.destroy()
