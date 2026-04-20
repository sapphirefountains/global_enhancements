import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def create_primary_contact_fields():
	doctypes = ["Project", "Opportunity", "Lead", "Supplier", "Account"]

	for doctype in doctypes:
		insert_after = get_insert_after_field(doctype)
		meta = frappe.get_meta(doctype)
		
		# We want to put the Enhanced Address & Contact at the bottom of the Contacts tab.
		tab_name = insert_after
		found_tab = False
		last_field_in_tab = tab_name
		our_fields = ["custom_address_and_contact_section", "custom_address_and_contact_html"]
		
		# Find the last standard field in the tab
		for field in meta.fields:
			if field.fieldname == tab_name:
				found_tab = True
				continue
			if found_tab:
				if field.fieldtype == "Tab Break":
					break
				if field.fieldname not in our_fields:
					last_field_in_tab = field.fieldname

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
			},
			{
				"fieldname": "custom_address_and_contact_section",
				"label": "Enhanced Address and Contact",
				"fieldtype": "Section Break",
				"insert_after": last_field_in_tab
			},
			{
				"fieldname": "custom_address_and_contact_html",
				"label": "Address and Contact HTML",
				"fieldtype": "HTML",
				"insert_after": "custom_address_and_contact_section"
			}
		]

		fields_to_process = []
		for field in all_fields:
			if meta.has_field(field["fieldname"]) and not frappe.db.exists("Custom Field", {"dt": doctype, "fieldname": field["fieldname"]}):
				continue
			fields_to_process.append(field)

		if fields_to_process:
			custom_fields = {doctype: fields_to_process}
			create_custom_fields(custom_fields, update=True)

		# FIX TOPOLOGICAL SORTING FOR CUSTOM TABS
		# If any Tab Break was inserted after `last_field_in_tab`, we need to change its `insert_after` to point to `custom_address_and_contact_html`
		# so it doesn't interleave its contents into our tab.
		custom_tabs = frappe.get_all("Custom Field", filters={"dt": doctype, "fieldtype": "Tab Break", "insert_after": last_field_in_tab})
		for tab in custom_tabs:
			frappe.db.set_value("Custom Field", tab.name, "insert_after", "custom_address_and_contact_html")

def get_insert_after_field(doctype):
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

	meta = frappe.get_meta(doctype)
	for field in meta.fields:
		if field.fieldtype == "Tab Break" and any(word in field.label.lower() for word in ["contact", "address"]):
			return field.fieldname

	for field in meta.fields:
		if field.fieldtype == "Tab Break":
			return field.fieldname

	return ""

