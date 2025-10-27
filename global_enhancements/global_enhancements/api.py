import frappe

@frappe.whitelist()
def search_users(search_term: str | None = None):
    """
    Searches for users based on a search term.
    Returns a list of dictionaries with 'value' (user email) and 'label' (Full Name).
    """
    filters = [
        ["enabled", "=", 1],
        ["user_type", "=", "System User"]
    ]
    if search_term:
        filters.append(["full_name", "like", f"%{search_term}%"])

    users = frappe.get_all(
        "User",
        filters=filters,
        fields=["name", "full_name"],
        limit_page_length=10
    )

    # The format is designed for easy use in frontend autocomplete libraries
    return [{"value": user.name, "label": user.full_name} for user in users]

