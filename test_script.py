import frappe
def get_links():
    meta = frappe.get_meta('Address')
    for d in meta.fields:
        if d.fieldtype == 'Table':
            print(f"Address Table: {d.fieldname} - {d.options}")
    
    meta = frappe.get_meta('Contact')
    for d in meta.fields:
        if d.fieldtype == 'Table':
            print(f"Contact Table: {d.fieldname} - {d.options}")

