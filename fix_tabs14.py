import sys
sys.path.insert(0, '/home/parker_bailey/frappe/my-bench/apps/frappe')
import frappe

frappe.init(site='site1.local', sites_path='/home/parker_bailey/frappe/my-bench/sites')
frappe.connect()

try:
    frappe.conf.developer_mode = 1
    
    # We should make sure "custom_details_tab" is in the doc layout
    # we already verified it's the first field.
    
    # Let's ensure standard custom_fields.py logic doesn't break this in the future
    # Update global_enhancements/setup/custom_fields.py so we don't need to do this manually
    pass
except Exception as e:
    print(f"Error: {e}")
finally:
    frappe.destroy()
