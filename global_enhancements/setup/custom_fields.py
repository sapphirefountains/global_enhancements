import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def create_unified_tabs():
	# Matrix for field injection:
	# Customer: Contacts (Y), Addresses (Y)
	# Supplier: Contacts (Y), Addresses (Y)
	# Contact: Contacts (N), Addresses (Y)
	# Opportunity: Contacts (Y), Addresses (Y)
	# Project: Contacts (Y), Addresses (Y)

	matrix = {
		"Customer": {"contacts": True, "addresses": True},
		"Supplier": {"contacts": True, "addresses": True},
		"Contact": {"contacts": False, "addresses": True},
		"Opportunity": {"contacts": True, "addresses": True},
		"Project": {"contacts": True, "addresses": True},
	}

	tab_map = {
		"Project": "custom_contacts__addresses",
		"Opportunity": "contact_info",
		"Customer": "contacts_and_addresses_tab",
		"Supplier": "contacts_and_addresses_tab",
	}

	for doctype, config in matrix.items():
		meta = frappe.get_meta(doctype)
		target_tab = tab_map.get(doctype)
		
		fields = []
		insert_after_contacts = None

		# Handle Tab Injection
		if target_tab:
			if not meta.has_field(target_tab):
				# Create the tab if it doesn't exist (Customer/Supplier case)
				last_tab = get_last_tab_fieldname(doctype)
				fields.append({
					"fieldname": target_tab,
					"label": "Contacts & Addresses",
					"fieldtype": "Tab Break",
					"insert_after": last_tab
				})
				insert_after_contacts = target_tab
			else:
				# Use existing tab
				insert_after_contacts = target_tab
		else:
			# Fallback for Contact doctype which doesn't have a tab map entry
			insert_after_contacts = get_last_tab_fieldname(doctype)

		prev_field = insert_after_contacts

		# IF Contacts (Y)
		if config["contacts"]:
			fields.extend([
				{
					"fieldname": "primary_contact",
					"label": "Primary Contact",
					"fieldtype": "Link",
					"options": "Contact",
					"insert_after": prev_field
				},
				{
					"fieldname": "section_break_contacts",
					"label": "Contact Directory",
					"fieldtype": "Section Break",
					"insert_after": "primary_contact"
				},
				{
					"fieldname": "contact_list_html",
					"label": "Contact List HTML",
					"fieldtype": "HTML",
					"insert_after": "section_break_contacts"
				}
			])
			prev_field = "contact_list_html"

		# IF Addresses (Y)
		if config["addresses"]:
			fields.extend([
				{
					"fieldname": "primary_address",
					"label": "Primary Address",
					"fieldtype": "Link",
					"options": "Address",
					"insert_after": "section_break_map" # Moved directly into Map section per Phase 5
				},
				{
					"fieldname": "section_break_map",
					"label": "Location",
					"fieldtype": "Section Break",
					"insert_after": prev_field
				},
				{
					"fieldname": "location_map_html",
					"label": "Location Map HTML",
					"fieldtype": "HTML",
					"insert_after": "section_break_map"
				}
			])

		# Skip creation if the fieldname already exists (Standard or Custom)
		fields_to_create = []
		for field in fields:
			# Special handling for primary_address which we want to update insert_after for
			if meta.has_field(field["fieldname"]):
				if field["fieldname"] == "primary_address":
					# Update custom field if it exists
					if frappe.db.exists("Custom Field", {"dt": doctype, "fieldname": "primary_address"}):
						frappe.db.set_value("Custom Field", {"dt": doctype, "fieldname": "primary_address"}, "insert_after", field["insert_after"])
				continue
			fields_to_create.append(field)

		if fields_to_create:
			create_custom_fields({doctype: fields_to_create}, update=True)


def get_last_tab_fieldname(doctype):
	"""Find the last Tab Break fieldname to insert our new tab after it."""
	meta = frappe.get_meta(doctype)
	tabs = [f.fieldname for f in meta.fields if f.fieldtype == "Tab Break"]
	if tabs:
		return tabs[-1]
	return None


def create_primary_contact_fields():
	create_unified_tabs()
