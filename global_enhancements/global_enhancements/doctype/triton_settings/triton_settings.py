# Copyright (c) 2026, Sapphire Fountains and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class TritonSettings(Document):
    def validate(self):
        if self.triton_base_url:
            self.triton_base_url = self.triton_base_url.strip().rstrip("/")

    def on_update(self):
        # The proxy caches resolved settings/tokens; bust them on save so a
        # changed URL or secret takes effect immediately.
        frappe.cache().delete_value("triton_settings_resolved")


@frappe.whitelist()
def test_connection():
    """Verify the configured Base URL + Gateway Secret by minting a bridge
    token for the current user. Surfaced from the Settings form menu."""
    frappe.only_for("System Manager")
    from global_enhancements.triton_chat import mint_user_token, get_settings

    settings = get_settings()
    if not settings.get("enabled"):
        return {"ok": False, "message": "Triton Assistant is disabled."}
    if not settings.get("base_url"):
        return {"ok": False, "message": "Triton Base URL is not set."}
    if not settings.get("gateway_secret"):
        return {"ok": False, "message": "Gateway Secret is not set."}

    try:
        token = mint_user_token(force_refresh=True)
        if token:
            return {"ok": True, "message": f"Connected. Token minted for {frappe.session.user}."}
        return {"ok": False, "message": "Triton did not return a token."}
    except Exception as e:
        return {"ok": False, "message": f"Connection failed: {e}"}
