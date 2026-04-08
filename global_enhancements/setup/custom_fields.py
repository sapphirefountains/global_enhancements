import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def create_primary_contact_fields():
	doctypes = ["Project", "Opportunity", "Lead", "Supplier", "Customer"]

	# The tab name varies across doctypes. E.g. Supplier has "Contacts & Addresses" tab.
	# We will try to insert after the respective tab break. If no tab break, just append to top.
	# Let's inspect the fields first or assume standard tab break names.
	# The goal is to insert these fields inside the relevant tab.
	# To make it robust, we will look for a Tab Break or Section Break named similar to Contact/Address.

	for doctype in doctypes:
		insert_after = get_insert_after_field(doctype)

		custom_fields = {
			doctype: [
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
				}
			]
		}
		create_custom_fields(custom_fields)


def get_insert_after_field(doctype):
	# Based on standard ERPNext/Frappe field names for the "Contacts & Address" tab
	tab_map = {
		"Lead": "tab_contact_info",
		"Opportunity": "tab_contact_info",
		"Supplier": "contact_and_address_tab",
		"Customer": "contact_and_address_tab",
		"Project": "users_and_contacts_tab", # Typically 'users_tab' or 'users_and_contacts_tab'
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
