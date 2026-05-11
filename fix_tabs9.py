import sys
sys.path.insert(0, '/home/parker_bailey/frappe/my-bench/apps/frappe')
import frappe

frappe.init(site='site1.local', sites_path='/home/parker_bailey/frappe/my-bench/sites')
frappe.connect()

try:
    # Now that Details is first in DocType, we need to update our custom fields injection script to not break it.
    # The custom fields script was injecting Contacts & Addresses BEFORE Details.
    # We already updated Contacts & Addresses to be inserted after tasks_html.
    
    frappe.db.set_value('Custom Field', 'Master Project-custom_contacts__addresses', 'insert_after', 'tasks_html')
    frappe.db.commit()
    print('Updated Contacts & Addresses position')
except Exception as e:
    print(f"Error: {e}")
finally:
    frappe.destroy()
