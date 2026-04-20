import frappe

PRIMARY_CONTACT_DOCTYPES = ["Project", "Opportunity", "Lead", "Supplier", "Accounts"]

def sync_from_main_doc(doc, method):
    if not getattr(doc, "primary_contact", None):
        return

    # If the user just selected a new primary contact, don't overwrite the contact
    # with the old form values that haven't been refreshed yet.
    is_new = getattr(doc, "is_new", None)
    if not (callable(is_new) and is_new()) and not (isinstance(is_new, bool) and is_new):
        old_doc = doc.get_doc_before_save()
        if old_doc and old_doc.primary_contact != doc.primary_contact:
            return

    contact = frappe.get_doc("Contact", doc.primary_contact)
    changed = False

    # Note: Full name is intrinsically linked as the link field. We don't try to sync "back"
    # a changed link field's string to first/last name, as the link field merely references the Contact.

    # Sync Job Title
    job_title = getattr(doc, "primary_contact_job_title", "") or ""
    if (contact.custom_title or "") != job_title:
        contact.custom_title = job_title
        changed = True

    # Sync Phone
    phone = getattr(doc, "primary_contact_phone", "") or ""
    if phone or (contact.phone and not phone):
        # Update existing primary phone, or add if it doesn't exist
        primary_phone_found = False
        for p in contact.get("phone_nos", []):
            if p.is_primary_phone:
                if (p.phone or "") != phone:
                    p.phone = phone
                    changed = True
                primary_phone_found = True
                break

        if not primary_phone_found and phone:
            contact.append("phone_nos", {"phone": phone, "is_primary_phone": 1})
            changed = True

        if (contact.phone or "") != phone:
            contact.phone = phone
            changed = True

    # Sync Email
    email = getattr(doc, "primary_contact_email", "") or ""
    if (contact.custom_email or "") != email:
        contact.custom_email = email
        changed = True

    if changed:
        contact.flags.ignore_permissions = True
        contact.flags.ignore_links = True
        contact.flags.is_syncing = True
        contact.save()

def sync_from_contact(doc, method):
    if getattr(doc.flags, "is_syncing", False):
        return

    job_title = doc.custom_title or ""
    phone = doc.phone or doc.mobile_no or ""
    email = doc.custom_email or ""

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
