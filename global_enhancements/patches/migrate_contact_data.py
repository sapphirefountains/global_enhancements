import frappe

def execute():
    """
    Migrates contact data, preserves primary contact links, 
    and migrates data from legacy child tables.
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

    # Step A: Scalar Field Migration (Customer & Project)
    migrate_scalar_links("Customer")
    migrate_scalar_links("Project")

    # Step B: Child Table Migration (custom_contacts__address_table / Project Stakeholder)
    migrate_project_stakeholders()

    # Step C: Legacy Address Field Migration
    migrate_legacy_address_fields()

    # Final Sweep for orphaned data in old fields
    sweep_orphaned_data()

def migrate_scalar_links(doctype):
    records = frappe.get_all(doctype, filters={"primary_contact": ["is", "set"]}, fields=["name", "primary_contact"])
    for doc in records:
        ensure_dynamic_link_and_primary(doc.primary_contact, doctype, doc.name)

def migrate_legacy_address_fields():
    """Migrates custom_customer__lead_address to primary_address for Customer and Lead."""
    for doctype in ["Customer", "Lead"]:
        if not frappe.db.exists("DocType", doctype):
            continue
            
        meta = frappe.get_meta(doctype)
        if meta.has_field("custom_customer__lead_address"):
            records = frappe.get_all(
                doctype, 
                filters={"custom_customer__lead_address": ["is", "set"]}, 
                fields=["name", "custom_customer__lead_address", "primary_address"]
            )
            
            for doc in records:
                # Only migrate if primary_address is not already set
                if not doc.primary_address:
                    frappe.db.set_value(doctype, doc.name, "primary_address", doc.custom_customer__lead_address, update_modified=False)
                
                # Also ensure the Address has a Dynamic Link to this record
                ensure_address_link(doc.custom_customer__lead_address, doctype, doc.name)

def migrate_project_stakeholders():
    """Migrates data from tabProject Stakeholder to the new Link-based system."""
    if not frappe.db.table_exists("Project Stakeholder"):
        return

    stakeholders = frappe.db.get_all(
        "Project Stakeholder", 
        fields=["name", "parent", "parenttype", "contact_person", "address", "role"]
    )

    for s in stakeholders:
        # 1. Migrate Contact
        if s.contact_person:
            ensure_dynamic_link_and_primary(
                s.contact_person, 
                s.parenttype, 
                s.parent, 
                is_primary=(s.role == "Primary Contact")
            )
            
            # If primary role, also update parent doc field
            if s.role == "Primary Contact":
                try:
                    parent_doc = frappe.get_doc(s.parenttype, s.parent)
                    parent_doc.primary_contact = s.contact_person
                    parent_doc.save(ignore_permissions=True, ignore_links=True)
                except Exception:
                    pass

        # 2. Migrate Address
        if s.address:
            ensure_address_link(s.address, s.parenttype, s.parent)
            
            # If primary role, also update parent doc field
            if s.role == "Primary Contact":
                try:
                    parent_doc = frappe.get_doc(s.parenttype, s.parent)
                    parent_doc.primary_address = s.address
                    parent_doc.save(ignore_permissions=True, ignore_links=True)
                except Exception:
                    pass

def ensure_dynamic_link_and_primary(contact_name, link_doctype, link_name, is_primary=True):
    if not frappe.db.exists("Contact", contact_name):
        return

    try:
        contact = frappe.get_doc("Contact", contact_name)
        
        link_exists = False
        for link in contact.links:
            if link.link_doctype == link_doctype and link.link_name == link_name:
                link_exists = True
                break
        
        changed = False
        if not link_exists:
            contact.append("links", {
                "link_doctype": link_doctype,
                "link_name": link_name
            })
            changed = True
        
        if is_primary:
            contact.is_primary_contact = 1
            changed = True
        
        if changed:
            contact.save(ignore_permissions=True, ignore_links=True)
    except Exception:
        pass

def ensure_address_link(address_name, link_doctype, link_name):
    if not frappe.db.exists("Address", address_name):
        return

    try:
        address = frappe.get_doc("Address", address_name)
        
        link_exists = False
        for link in address.links:
            if link.link_doctype == link_doctype and link.link_name == link_name:
                link_exists = True
                break
        
        if not link_exists:
            address.append("links", {
                "link_doctype": link_doctype,
                "link_name": link_name
            })
            address.save(ignore_permissions=True, ignore_links=True)
    except Exception:
        pass

def sweep_orphaned_data():
    main_doctypes = ["Project", "Opportunity", "Supplier", "Customer"]
    for dt in main_doctypes:
        if not frappe.db.exists("DocType", dt):
            continue
        
        meta = frappe.get_meta(dt)
        fields_to_check = {
            "primary_contact_phone": "custom_phone_number",
            "primary_contact_email": "custom_email",
            "primary_contact_job_title": "custom_title"
        }
        
        existing_fields = [f for f in fields_to_check.keys() if meta.has_field(f)]
        if not existing_fields:
            continue

        query_fields = ["name", "primary_contact"] + existing_fields
        docs = frappe.db.get_all(dt, fields=query_fields)
        
        for doc in docs:
            if not doc.primary_contact:
                continue
            
            try:
                contact = frappe.get_doc("Contact", doc.primary_contact)
                changed = False
                
                for old_f, new_f in fields_to_check.items():
                    if meta.has_field(old_f) and doc.get(old_f) and not contact.get(new_f):
                        contact.set(new_f, doc.get(old_f))
                        changed = True
                
                if changed:
                    contact.save(ignore_permissions=True, ignore_links=True)
            except Exception:
                continue
