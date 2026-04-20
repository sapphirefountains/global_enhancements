import frappe
def print_cf():
    cfs = frappe.get_all("Custom Field", filters={"dt": ("in", ["Project", "Opportunity", "Lead", "Supplier", "Account"])}, fields=["name", "dt", "fieldname"])
    for cf in cfs:
        print(f"{cf.dt} - {cf.fieldname} ({cf.name})")
