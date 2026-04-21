import frappe

PRIMARY_CONTACT_DOCTYPES = ["Project", "Opportunity", "Supplier", "Customer"]

def sync_from_main_doc(doc, method):
    if not getattr(doc, "primary_contact", None):
        return

    is_new = getattr(doc, "is_new", None)
    if not (callable(is_new) and is_new()) and not (isinstance(is_new, bool) and is_new):
        old_doc = doc.get_doc_before_save()
        if old_doc and old_doc.primary_contact != doc.primary_contact:
            return

    try:
        contact = frappe.get_doc("Contact", doc.primary_contact)
    except frappe.DoesNotExistError:
        return

    changed = False

    # Sync Title
    title = getattr(doc, "primary_contact_job_title", None)
    if title is not None and (contact.custom_title or "") != title:
        contact.custom_title = title
        changed = True

    # Sync Phone
    phone = getattr(doc, "primary_contact_phone", None)
    if phone is not None and (contact.custom_phone_number or "") != phone:
        if phone: # Prevent wiping out contact data during transition
            contact.custom_phone_number = phone
            changed = True

    # Sync Email
    email = getattr(doc, "primary_contact_email", None)
    if email is not None and (contact.custom_email or "") != email:
        if email: # Prevent wiping out contact data during transition
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

    custom_title = doc.custom_title or ""
    custom_phone = doc.custom_phone_number or ""
    custom_mobile = doc.custom_mobile_number or ""
    custom_email = doc.custom_email or ""
    
    phone_to_sync = custom_phone or custom_mobile

    for dt in PRIMARY_CONTACT_DOCTYPES:
        linked_docs = frappe.get_all(dt, filters={"primary_contact": doc.name})
        for linked in linked_docs:
            main_doc = frappe.get_doc(dt, linked.name)

            main_changed = False
            if hasattr(main_doc, "primary_contact_job_title") and main_doc.primary_contact_job_title != custom_title:
                main_doc.primary_contact_job_title = custom_title
                main_changed = True
            if hasattr(main_doc, "primary_contact_phone") and main_doc.primary_contact_phone != phone_to_sync:
                main_doc.primary_contact_phone = phone_to_sync
                main_changed = True
            if hasattr(main_doc, "primary_contact_email") and main_doc.primary_contact_email != custom_email:
                main_doc.primary_contact_email = custom_email
                main_changed = True

            if main_changed:
                main_doc.flags.ignore_permissions = True
                main_doc.save()
