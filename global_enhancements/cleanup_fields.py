import frappe

def cleanup():
    fields_to_delete = [
        "primary_contact_section",
        "primary_contact",
        "primary_contact_job_title",
        "primary_contact_col_break",
        "primary_contact_phone",
        "primary_contact_email",
        "address_and_contact",
        "address_html",
        "contact_html",
        "custom_contact_info_tab"
    ]

    doctypes = ["Project", "Opportunity", "Lead", "Supplier", "Account"]

    for dt in doctypes:
        for fd in fields_to_delete:
            cf_name = f"{dt}-{fd}"
            if frappe.db.exists("Custom Field", cf_name):
                frappe.delete_doc("Custom Field", cf_name, ignore_permissions=True)
                print(f"Deleted {cf_name}")

