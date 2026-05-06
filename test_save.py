import frappe
def test():
    doc = frappe.get_doc("Supplier", "Valley View Granite")
    doc.supplier_group = "3D Printing" # Change it
    doc.save()
    updated_doc = frappe.get_doc("Supplier", "Valley View Granite")
    print(f"Updated search field: {updated_doc.custom_supplier_groups_search}")

