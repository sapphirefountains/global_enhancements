import sys
sys.path.insert(0, '/home/parker_bailey/frappe/my-bench/apps/frappe')
import frappe

frappe.init(site='site1.local', sites_path='/home/parker_bailey/frappe/my-bench/sites')
frappe.connect()

try:
    frappe.conf.developer_mode = 1
    
    doc = frappe.get_doc("DocType", "Master Project")
    
    # We want field_order to be: custom_details_tab, title, description, projects_html, tasks_html
    new_fields = []
    
    details_tab = None
    for f in doc.fields:
        if f.fieldname == 'custom_details_tab':
            details_tab = f
            break
            
    if details_tab:
        new_fields.append(details_tab)
        
    for f in doc.fields:
        if f.fieldname != 'custom_details_tab':
            new_fields.append(f)
            
    doc.fields = new_fields
    doc.save()
    
    frappe.db.commit()
    print('Success')
except Exception as e:
    print(f"Error: {e}")
finally:
    frappe.destroy()
