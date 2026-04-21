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

	for doctype, config in matrix.items():
		insert_after = get_last_tab_fieldname(doctype)

		fields = []

		# ALWAYS INJECT: contacts_and_addresses_tab
		fields.append({
			"fieldname": "contacts_and_addresses_tab",
			"label": "Contacts & Addresses",
			"fieldtype": "Tab Break",
			"insert_after": insert_after
		})

		prev_field = "contacts_and_addresses_tab"

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
					"insert_after": prev_field
				},
				{
					"fieldname": "section_break_map",
					"label": "Location",
					"fieldtype": "Section Break",
					"insert_after": "primary_address"
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
		meta = frappe.get_meta(doctype)
		for field in fields:
			if meta.has_field(field["fieldname"]):
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
	# Keep this for backward compatibility if needed, but redirects to the new logic
	create_unified_tabs()
