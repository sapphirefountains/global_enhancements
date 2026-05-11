import sys
import json
import frappe

def run():
    try:
        frappe.init(site='site1.local', sites_path='/home/parker_bailey/frappe/my-bench/sites')
        frappe.connect()
        doc = frappe.get_doc('DocType', 'Master Project')
        fields = [{'fieldname': getattr(f, 'fieldname', ''), 'fieldtype': getattr(f, 'fieldtype', ''), 'label': getattr(f, 'label', '')} for f in doc.fields]
        print(json.dumps(fields, indent=2))
    except Exception as e:
        print(f"Error: {e}")
    finally:
        frappe.destroy()

if __name__ == '__main__':
    run()
