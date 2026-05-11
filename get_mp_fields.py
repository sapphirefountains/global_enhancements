import sys
sys.path.insert(0, '/home/parker_bailey/frappe/my-bench/apps/frappe')
import frappe
import json

frappe.init(site='site1.local', sites_path='/home/parker_bailey/frappe/my-bench/sites')
frappe.connect()

def get_data():
    try:
        doc = frappe.get_doc('DocType', 'Master Project')
        fields = []
        for f in doc.fields:
            fields.append({
                'fieldname': getattr(f, 'fieldname', ''),
                'fieldtype': getattr(f, 'fieldtype', ''),
                'label': getattr(f, 'label', '')
            })
        print(json.dumps(fields, indent=2))
    except Exception as e:
        print(f"Error: {e}")

get_data()
