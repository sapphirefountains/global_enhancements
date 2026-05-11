import sys
sys.path.insert(0, '/home/parker_bailey/frappe/my-bench/apps/frappe')
import frappe
frappe.init(site='site1.local', sites_path='/home/parker_bailey/frappe/my-bench/sites')
frappe.connect()

meta = frappe.get_meta('Master Project')
for i, f in enumerate(meta.fields):
    print(f"{i}: {f.fieldname} ({f.fieldtype})")
