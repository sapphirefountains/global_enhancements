import sys
sys.path.insert(0, '/home/parker_bailey/frappe/my-bench/apps/frappe')
import frappe
from frappe.core.doctype.custom_field.custom_field import export_custom_fields

frappe.init(site='site1.local', sites_path='/home/parker_bailey/frappe/my-bench/sites')
frappe.connect()

export_custom_fields()
print("Exported custom fields")
