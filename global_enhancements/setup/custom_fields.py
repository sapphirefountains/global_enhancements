import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def create_primary_contact_fields():
	doctypes = ["Project", "Opportunity", "Lead", "Supplier", "Account"]

	# The tab name varies across doctypes. E.g. Supplier has "Contacts & Addresses" tab.
	# We will try to insert after the respective tab break. If no tab break, just append to top.
	# Let's inspect the fields first or assume standard tab break names.
	# The goal is to insert these fields inside the relevant tab.
	# To make it robust, we will look for a Tab Break or Section Break named similar to Contact/Address.

	for doctype in doctypes:
		insert_after = get_insert_after_field(doctype)

		all_fields = [
			{
				"fieldname": "primary_contact_section",
				"label": "Primary Contact",
				"fieldtype": "Section Break",
				"insert_after": insert_after
			},
			{
				"fieldname": "primary_contact",
				"label": "Full Name",
				"fieldtype": "Link",
				"options": "Contact",
				"insert_after": "primary_contact_section"
			},
			{
				"fieldname": "primary_contact_job_title",
				"label": "Job Title",
				"fieldtype": "Data",
				"insert_after": "primary_contact",
			},
			{
				"fieldname": "primary_contact_col_break",
				"fieldtype": "Column Break",
				"insert_after": "primary_contact_job_title"
			},
			{
				"fieldname": "primary_contact_phone",
				"label": "Phone",
				"fieldtype": "Data",
				"insert_after": "primary_contact_col_break"
			},
			{
				"fieldname": "primary_contact_email",
				"label": "Email Address",
				"fieldtype": "Data",
				"insert_after": "primary_contact_phone"
			},
			{
				"fieldname": "address_and_contact",
				"label": "Address and Contact",
				"fieldtype": "HTML",
				"insert_after": "primary_contact_email"
			}
		]

		fields_to_process = []
		meta = frappe.get_meta(doctype)
		for field in all_fields:
			# If the field exists but is NOT a Custom Field, it is a Standard Field.
			# We must skip it to avoid a validation error during creation.
			if meta.has_field(field["fieldname"]) and not frappe.db.exists("Custom Field", {"dt": doctype, "fieldname": field["fieldname"]}):
				continue
			fields_to_process.append(field)

		if fields_to_process:
			custom_fields = {doctype: fields_to_process}
			create_custom_fields(custom_fields, update=True)


def get_insert_after_field(doctype):
	# Based on standard ERPNext/Frappe field names for the "Contacts & Address" tab
	tab_map = {
		"Lead": "custom_contacts__addresses_personal",
		"Opportunity": "contact_info",
		"Supplier": "contact_and_address_tab",
		"Account": "contact_and_address_tab",
		"Project": "custom_contacts__addresses",
	}

	target_tab = tab_map.get(doctype)
	if target_tab and frappe.get_meta(doctype).has_field(target_tab):
		return target_tab

	# Fallback: find the first tab that sounds like contacts/addresses
	meta = frappe.get_meta(doctype)
	for field in meta.fields:
		if field.fieldtype == "Tab Break" and any(word in field.label.lower() for word in ["contact", "address"]):
			return field.fieldname

	# Final fallback
	for field in meta.fields:
		if field.fieldtype == "Tab Break":
			return field.fieldname

	return ""
