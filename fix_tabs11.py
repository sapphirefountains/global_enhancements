import sys
sys.path.insert(0, '/home/parker_bailey/frappe/my-bench/apps/frappe')
import frappe

frappe.init(site='site1.local', sites_path='/home/parker_bailey/frappe/my-bench/sites')
frappe.connect()

try:
    frappe.conf.developer_mode = 1
    # Move standard fields down
    doc = frappe.get_doc("DocType", "Master Project")
    for f in doc.fields:
        if f.fieldname in ['title', 'description', 'projects_html', 'tasks_html']:
            f.insert_after = 'custom_details_tab'
    doc.save()
    frappe.db.commit()
    print('Updated standard field insert_after')
except Exception as e:
    print(f"Error: {e}")
finally:
    frappe.destroy()
