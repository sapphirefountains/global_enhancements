import sys
sys.path.insert(0, '/home/parker_bailey/frappe/my-bench/apps/frappe')
import frappe

frappe.init(site='site1.local', sites_path='/home/parker_bailey/frappe/my-bench/sites')
frappe.connect()

frappe.conf.developer_mode = 1

doc = frappe.get_doc("DocType", "Master Project")
# Remove all custom_details_tab fields
doc.fields = [f for f in doc.fields if f.fieldname != 'custom_details_tab']

doc.append('fields', {
    'fieldname': 'custom_details_tab',
    'label': 'Details',
    'fieldtype': 'Tab Break'
})

new_fields = []
new_fields.append(doc.fields[-1])
for f in doc.fields[:-1]:
    new_fields.append(f)

doc.fields = new_fields
doc.save()
frappe.db.commit()

# Delete duplicate custom fields if any
frappe.db.sql("DELETE FROM tabDocField WHERE parent='Master Project' AND fieldname='custom_details_tab' AND idx > 0")
frappe.db.commit()

