import frappe

PRIMARY_CONTACT_DOCTYPES = ["Project", "Opportunity", "Lead", "Supplier", "Customer"]

def sync_from_main_doc(doc, method):
    if not getattr(doc, "primary_contact", None):
        return

    contact = frappe.get_doc("Contact", doc.primary_contact)
    changed = False

    # Note: Full name is intrinsically linked as the link field. We don't try to sync "back"
    # a changed link field's string to first/last name, as the link field merely references the Contact.

    # Sync Job Title
    job_title = getattr(doc, "primary_contact_job_title", "") or ""
    if contact.designation != job_title:
        contact.designation = job_title
        changed = True

    # Sync Phone
    phone = getattr(doc, "primary_contact_phone", "") or ""
    if phone:
        # Update existing primary phone, or add if it doesn't exist
        primary_phone_found = False
        for p in contact.get("phone_nos", []):
            if p.is_primary_phone:
                if p.phone != phone:
                    p.phone = phone
                    changed = True
                primary_phone_found = True
                break

        if not primary_phone_found:
            contact.append("phone_nos", {"phone": phone, "is_primary_phone": 1})
            changed = True

        if contact.phone != phone:
            contact.phone = phone
            changed = True

    # Sync Email
    email = getattr(doc, "primary_contact_email", "") or ""
    if email:
        # Update existing primary email, or add if it doesn't exist
        primary_email_found = False
        for e in contact.get("email_ids", []):
            if e.is_primary:
                if e.email_id != email:
                    e.email_id = email
                    changed = True
                primary_email_found = True
                break

        if not primary_email_found:
            contact.append("email_ids", {"email_id": email, "is_primary": 1})
            changed = True

        if contact.email_id != email:
            contact.email_id = email
            changed = True

    if changed:
        contact.flags.ignore_permissions = True
        contact.flags.ignore_links = True
        contact.flags.is_syncing = True
        contact.save()

def sync_from_contact(doc, method):
    if getattr(doc.flags, "is_syncing", False):
        return

    job_title = doc.designation or ""
    phone = doc.phone or doc.mobile_no or ""
    email = doc.email_id or ""

    for dt in PRIMARY_CONTACT_DOCTYPES:
        # Find all documents linking to this contact
        linked_docs = frappe.get_all(dt, filters={"primary_contact": doc.name})
        for linked in linked_docs:
            main_doc = frappe.get_doc(dt, linked.name)

            main_changed = False
            # Full Name is implicit in the Link field display
            if main_doc.primary_contact_job_title != job_title:
                main_doc.primary_contact_job_title = job_title
                main_changed = True
            if main_doc.primary_contact_phone != phone:
                main_doc.primary_contact_phone = phone
                main_changed = True
            if main_doc.primary_contact_email != email:
                main_doc.primary_contact_email = email
                main_changed = True

            if main_changed:
                main_doc.flags.ignore_permissions = True
                main_doc.save()
