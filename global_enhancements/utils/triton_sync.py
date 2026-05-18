import frappe
import requests

def global_triton_sync(doc, method=None):
    SYNC_WHITELIST = [
        "Sales Order", "Lead", "Project", "Task", "Customer", "Opportunity", "File",
        "Quotation", "Item", "Supplier", "Contact", "Address", "Comment", "Accounts",
        "Note", "CRM", "CRM Note", "Delivery Note", "Sales Invoice", "Issue"
    ]
    if doc.doctype not in SYNC_WHITELIST:
        return
    TRITON_URL = "https://triton.sapphirefountains.com/api/v1/webhooks/frappe-webhook"
    try:
        payload = {
            "doctype": doc.doctype,
            "name": doc.name,
            "user_id": 1
        }
        frappe.enqueue(
            'requests.post',
            url=TRITON_URL,
            json=payload,
            now=False,
            queue='default'
        )
    except Exception as e:
        frappe.log_error(f"Triton Sync Error: {str(e)}", "Triton Webhook")
