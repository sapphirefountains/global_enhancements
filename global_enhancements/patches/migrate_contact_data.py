import frappe

def execute():
    """
    Migrates contact data and preserves primary contact links for Customer and Project records.
    """
    # 1. Migrate Contact DocType standard fields to custom fields
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

    # 2. Customer Migration: Preserve primary_contact links
    customers = frappe.get_all("Customer", filters={"primary_contact": ["is", "set"]}, fields=["name", "primary_contact"])
    for customer in customers:
        ensure_dynamic_link_and_primary(customer.primary_contact, "Customer", customer.name)

    # 3. Project Migration: Preserve primary_contact links
    projects = frappe.get_all("Project", filters={"primary_contact": ["is", "set"]}, fields=["name", "primary_contact"])
    for project in projects:
        ensure_dynamic_link_and_primary(project.primary_contact, "Project", project.name)

    # 4. Sweep Main DocTypes for orphaned data in old fields
    main_doctypes = ["Project", "Opportunity", "Supplier", "Customer"]
    for dt in main_doctypes:
        if not frappe.db.exists("DocType", dt):
            continue
        
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
                
                if has_phone and doc.get("primary_contact_phone") and not contact.custom_phone_number:
                    contact_updates["custom_phone_number"] = doc.primary_contact_phone
                
                if has_email and doc.get("primary_contact_email") and not contact.custom_email:
                    contact_updates["custom_email"] = doc.primary_contact_email
                    
                if has_title and doc.get("primary_contact_job_title") and not contact.custom_title:
                    contact_updates["custom_title"] = doc.primary_contact_job_title
                    
                if contact_updates:
                    frappe.db.set_value("Contact", contact.name, contact_updates, update_modified=False)
            except Exception:
                continue

def ensure_dynamic_link_and_primary(contact_name, link_doctype, link_name):
    """Ensures a Dynamic Link exists and sets is_primary_contact=1."""
    if not frappe.db.exists("Contact", contact_name):
        return

    contact = frappe.get_doc("Contact", contact_name)
    
    # Check if link already exists
    link_exists = False
    for link in contact.links:
        if link.link_doctype == link_doctype and link.link_name == link_name:
            link_exists = True
            break
    
    if not link_exists:
        contact.append("links", {
            "link_doctype": link_doctype,
            "link_name": link_name
        })
    
    contact.is_primary_contact = 1
    
    try:
        contact.save(ignore_permissions=True)
    except Exception:
        # Log error or skip if save fails due to other validation errors
        pass
