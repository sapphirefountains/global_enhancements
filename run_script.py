import frappe
import json

def run():
    doc = frappe.get_doc('DocType', 'Master Project')
    fields = [{'fieldname': f.fieldname, 'label': f.label, 'fieldtype': f.fieldtype} for f in doc.fields]
    print(json.dumps(fields, indent=2))
