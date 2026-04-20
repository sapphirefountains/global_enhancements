import frappe

@frappe.whitelist()
def add_link(link_doctype, link_name, doctype, name):
	doc = frappe.get_doc(doctype, name)
	
	# Check if link already exists to avoid duplicates
	for link in doc.get("links"):
		if link.link_doctype == link_doctype and link.link_name == link_name:
			return
			
	doc.append("links", {
		"link_doctype": link_doctype,
		"link_name": link_name
	})
	doc.save(ignore_permissions=True)

@frappe.whitelist()
def remove_link(link_doctype, link_name, doctype, name):
	doc = frappe.get_doc(doctype, name)
	removed = False
	
	# We need to find the specific link in the child table
	new_links = []
	for link in doc.get("links"):
		if link.link_doctype == link_doctype and link.link_name == link_name:
			removed = True
			continue
		new_links.append(link)
	
	if removed:
		doc.set("links", new_links)
		doc.save(ignore_permissions=True)
