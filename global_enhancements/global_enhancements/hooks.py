import frappe
import re
from frappe.utils import get_url_to_form

def process_mentions_on_update(doc, method):
    """
    Parse all Text Editor fields in a document on save, find new mentions,
    and create notifications.
    """
    # Regex to find user links: <a href="/app/user/user@email.com">...</a>
    mention_regex = re.compile(r'<a href="/app/user/([^"]+)">')

    # Get the document before it was saved to compare changes
    doc_before_save = doc.get_doc_before_save()
    if not doc_before_save:
        return

    # Find all fields of type 'Text Editor' in the document's meta
    text_editor_fields = [df.fieldname for df in doc.meta.get("fields") if df.fieldtype == "Text Editor"]

    if not text_editor_fields:
        return

    newly_mentioned_users = set()

    for fieldname in text_editor_fields:
        content_before = doc_before_save.get(fieldname) or ""
        content_after = doc.get(fieldname) or ""

        # Only proceed if the content has actually changed
        if content_before == content_after:
            continue

        mentions_before = set(mention_regex.findall(content_before))
        mentions_after = set(mention_regex.findall(content_after))

        # Find users that were just added in this save
        newly_mentioned_users.update(mentions_after - mentions_before)

    if not newly_mentioned_users:
        return

    # Prepare notification details
    current_user_fullname = frappe.utils.get_fullname(frappe.session.user)
    doc_label = doc.meta.get_label() or doc.doctype
    doc_name = doc.get_title() or doc.name

    subject = f"{current_user_fullname} mentioned you in {doc_label}: {doc_name}"
    document_url = get_url_to_form(doc.doctype, doc.name)

    # Create a notification for each newly mentioned user
    for user_email in newly_mentioned_users:
        # Avoid notifying the user who made the mention
        if user_email == frappe.session.user:
            continue

        notification_doc = {
            "doctype": "Notification Log",
            "for_user": user_email,
            "type": "Mention",
            "document_type": doc.doctype,
            "document_name": doc.name,
            "subject": subject,
            "email_content": f"<p>Hi,</p><p>{current_user_fullname} mentioned you in a document.</p>" \
                             f'<p><a href="{document_url}">Click here to view it.</a></p>'
        }
        frappe.get_doc(notification_doc).insert(ignore_permissions=True)
        
    # Commit changes to the database
    frappe.db.commit()
