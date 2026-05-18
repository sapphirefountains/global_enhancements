import frappe
from frappe import _


@frappe.whitelist()
def unlink_and_delete(doctype, name):
	"""
	Clear every link field that points to `name` of `doctype`, then delete the document.

	Handles:
	- Regular Link fields in standard doctypes
	- Link fields inside child tables
	- Dynamic Link fields (fieldtype = "Dynamic Link")
	"""
	if not frappe.has_permission(doctype, "delete", name):
		frappe.throw(_("You do not have permission to delete {0} {1}").format(doctype, name))

	_clear_link_fields(doctype, name)
	_clear_dynamic_link_fields(doctype, name)

	frappe.db.commit()

	# force=1 skips the link check so any remaining dynamic links don't block deletion
	frappe.delete_doc(doctype, name, force=1, ignore_permissions=True)

	return {"success": True}


def _clear_link_fields(doctype, name):
	"""Null out every Link field in every doctype that currently points to `name`."""
	link_fields = frappe.db.get_all(
		"DocField",
		filters={"fieldtype": "Link", "options": doctype},
		fields=["parent", "fieldname"],
	)

	for lf in link_fields:
		parent_dt = lf["parent"]
		fieldname = lf["fieldname"]

		try:
			# get_all raises if the table doesn't exist (e.g. virtual doctypes)
			records = frappe.db.get_all(
				parent_dt,
				filters={fieldname: name},
				fields=["name"],
				limit_page_length=0,
			)
		except Exception:
			continue

		for rec in records:
			try:
				frappe.db.set_value(parent_dt, rec["name"], fieldname, None)
			except Exception:
				frappe.log_error(
					frappe.get_traceback(),
					f"unlink_and_delete: could not clear {parent_dt}.{fieldname} = {rec['name']}",
				)


def _clear_dynamic_link_fields(doctype, name):
	"""
	Null out Dynamic Link fields whose paired doctype selector currently equals `doctype`
	and whose value equals `name`.
	"""
	dynamic_fields = frappe.db.get_all(
		"DocField",
		filters={"fieldtype": "Dynamic Link"},
		# options = fieldname of the sibling field that stores the linked doctype name
		fields=["parent", "fieldname", "options"],
	)

	for df in dynamic_fields:
		parent_dt = df["parent"]
		value_field = df["fieldname"]
		doctype_field = df["options"]

		if not doctype_field:
			continue

		try:
			records = frappe.db.get_all(
				parent_dt,
				filters={doctype_field: doctype, value_field: name},
				fields=["name"],
				limit_page_length=0,
			)
		except Exception:
			continue

		for rec in records:
			try:
				frappe.db.set_value(parent_dt, rec["name"], value_field, None)
				frappe.db.set_value(parent_dt, rec["name"], doctype_field, None)
			except Exception:
				frappe.log_error(
					frappe.get_traceback(),
					f"unlink_and_delete: could not clear dynamic link {parent_dt}.{value_field} = {rec['name']}",
				)
