import sys
sys.path.insert(0, '/home/parker_bailey/frappe/my-bench/apps/frappe')
import frappe

frappe.init(site='site1.local', sites_path='/home/parker_bailey/frappe/my-bench/sites')
frappe.connect()

try:
    frappe.conf.developer_mode = 1
    doc = frappe.get_doc("DocType", "Master Project")
    
    # We want Details Tab -> Title -> Description -> Projects -> Tasks
    # Make sure we don't have multiple custom_details_tabs
    new_fields = []
    has_details = False
    
    for f in doc.fields:
        if f.fieldname == 'custom_details_tab':
            if not has_details:
                new_fields.append(f)
                has_details = True
        else:
            new_fields.append(f)
            
    doc.fields = new_fields
    
    # Let's verify the order.
    fieldnames = [f.fieldname for f in doc.fields]
    if 'custom_details_tab' in fieldnames:
        idx = fieldnames.index('custom_details_tab')
        if idx != 0:
            # move it to index 0
            details = doc.fields.pop(idx)
            doc.fields.insert(0, details)
            
    doc.save()
    frappe.db.commit()
    print('Fixed Master Project standard fields')
except Exception as e:
    print(f"Error: {e}")
finally:
    frappe.destroy()
