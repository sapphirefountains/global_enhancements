import frappe
def print_fields():
    meta = frappe.get_meta('Opportunity')
    for i, d in enumerate(meta.fields):
        print(f"{i}: {d.fieldname} ({d.fieldtype}) - {d.label}")
