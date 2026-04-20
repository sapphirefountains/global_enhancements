import frappe
def check():
    pss = frappe.get_all("Property Setter", filters={"doc_type": ("in", ["Opportunity", "Project", "Lead", "Supplier", "Account"])}, fields=["name", "doc_type", "field_name", "property", "value"])
    for ps in pss:
        if ps.property in ["insert_after", "hidden", "print_hide"]:
            print(f"{ps.doc_type} - {ps.field_name} - {ps.property} = {ps.value}")
