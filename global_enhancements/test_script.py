import frappe
def test_fields():
    for dt in ["Project", "Opportunity", "Lead", "Supplier", "Account"]:
        meta = frappe.get_meta(dt)
        print(f"DocType '{dt}':")
        print("  address_html:", meta.has_field('address_html'))
        print("  contact_html:", meta.has_field('contact_html'))

