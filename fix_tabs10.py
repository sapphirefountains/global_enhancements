import sys
sys.path.insert(0, '/home/parker_bailey/frappe/my-bench/apps/frappe')
import frappe

frappe.init(site='site1.local', sites_path='/home/parker_bailey/frappe/my-bench/sites')
frappe.connect()

try:
    doc = frappe.get_doc("DocType", "Master Project")
    print(f"First field is: {doc.fields[0].fieldname}")
    
    # Check if there is any other 'custom_details_tab' in Custom Field table
    # Sometimes standard fields clash with custom fields of the same name
    cf = frappe.db.exists("Custom Field", "Master Project-custom_details_tab")
    if cf:
        print(f"Found Custom Field {cf}, deleting...")
        frappe.delete_doc("Custom Field", cf)
        frappe.db.commit()
    else:
        print("No Custom Field for custom_details_tab found.")

except Exception as e:
    print(f"Error: {e}")
finally:
    frappe.destroy()
