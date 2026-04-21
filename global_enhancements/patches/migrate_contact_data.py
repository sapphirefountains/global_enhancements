import frappe

def execute():
    """
    Migrates contact data from standard phone/mobile fields and old main doc custom fields 
    into the new universal custom fields on the Contact DocType.
    """
    # 1. Migrate Contact DocType standard fields to custom fields
    # We use frappe.db.get_all so it doesn't fail if the custom fields aren't completely patched yet
    contacts = frappe.db.get_all(
        "Contact", 
        fields=["name", "phone", "mobile_no", "custom_phone_number", "custom_mobile_number"]
    )
    
    for c in contacts:
        updates = {}
        if c.phone and not c.custom_phone_number:
            updates["custom_phone_number"] = c.phone
        if c.mobile_no and not c.custom_mobile_number:
            updates["custom_mobile_number"] = c.mobile_no
        
        if updates:
            frappe.db.set_value("Contact", c.name, updates, update_modified=False)

    # 2. Sweep Main DocTypes for orphaned data in old fields
    main_doctypes = ["Project", "Opportunity", "Supplier", "Customer"]
    for dt in main_doctypes:
        if not frappe.db.exists("DocType", dt):
            continue
        
        # Check if the old fields actually exist in the DB schema for this doctype
        meta = frappe.get_meta(dt)
        has_phone = meta.has_field("primary_contact_phone")
        has_email = meta.has_field("primary_contact_email")
        has_title = meta.has_field("primary_contact_job_title")

        if not (has_phone or has_email or has_title):
            continue

        fields = ["name", "primary_contact"]
        if has_phone: fields.append("primary_contact_phone")
        if has_email: fields.append("primary_contact_email")
        if has_title: fields.append("primary_contact_job_title")

        docs = frappe.db.get_all(dt, fields=fields)
        for doc in docs:
            if not doc.primary_contact:
                continue
            
            try:
                contact = frappe.get_doc("Contact", doc.primary_contact)
                contact_updates = {}
                
                # If main doc had a phone, and the contact's custom phone is blank, grab it
                if has_phone and doc.get("primary_contact_phone") and not contact.custom_phone_number:
                    contact_updates["custom_phone_number"] = doc.primary_contact_phone
                
                # If main doc had an email, and the contact's custom email is blank, grab it
                if has_email and doc.get("primary_contact_email") and not contact.custom_email:
                    contact_updates["custom_email"] = doc.primary_contact_email
                    
                # If main doc had a title, and the contact's custom title is blank, grab it
                if has_title and doc.get("primary_contact_job_title") and not contact.custom_title:
                    contact_updates["custom_title"] = doc.primary_contact_job_title
                    
                if contact_updates:
                    frappe.db.set_value("Contact", contact.name, contact_updates, update_modified=False)
            except Exception:
                # If Contact doc is broken or doesn't exist anymore, just skip gracefully
                continue
