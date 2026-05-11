import sys
sys.path.insert(0, '/home/parker_bailey/frappe/my-bench/apps/frappe')
import frappe

frappe.init(site='site1.local', sites_path='/home/parker_bailey/frappe/my-bench/sites')
frappe.connect()

doc = frappe.get_meta('Master Project')
for f in doc.fields:
    if f.fieldname == 'title':
        print(f"Title field is under tab: {f.get('tab_break')}")
        break
