import sys
sys.path.insert(0, '/home/parker_bailey/frappe/my-bench/apps/frappe')
import frappe

frappe.init(site='site1.local', sites_path='/home/parker_bailey/frappe/my-bench/sites')
frappe.connect()

try:
    frappe.conf.developer_mode = 1
    doc = frappe.get_doc("DocType", "Master Project")
    
    # In ERPNext, the layout is determined strictly by the order of fields in the doc.fields list.
    # The first Tab Break defines the start of the tabs. Any fields before the first Tab Break
    # are shown outside/above the tabs.
    # Let's ensure custom_details_tab is the VERY FIRST field in the list.
    
    new_fields = []
    
    # 1. Add Details Tab
    details_tab = None
    for f in doc.fields:
        if f.fieldname == 'custom_details_tab':
            details_tab = f
            break
            
    if details_tab:
        new_fields.append(details_tab)
        
    # 2. Add the rest of the fields
    for f in doc.fields:
        if f.fieldname != 'custom_details_tab':
            new_fields.append(f)
            
    doc.fields = new_fields
    doc.save()
    frappe.db.commit()
    print('Fixed Master Project standard fields')
except Exception as e:
    print(f"Error: {e}")
finally:
    frappe.destroy()
