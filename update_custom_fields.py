import sys
sys.path.insert(0, '/home/parker_bailey/frappe/my-bench/apps/frappe')
import frappe

frappe.init(site='site1.local', sites_path='/home/parker_bailey/frappe/my-bench/sites')
frappe.connect()

try:
    # 1. We want Details to be first. Since standard fields are processed before Custom Fields,
    # and we made Details a standard field and put it first, that part is done.
    
    # 2. We need to move Custom Fields that don't deal with address/contacts to be UNDER the Details tab.
    # What are the standard fields? Title, Description, Projects, Tasks. These are automatically under Details now.
    
    # Wait, the prompt says "remove everything that doesn't deal with address and contacts and take them out of the Contacts & Addresses tab and move it over to the details tab".
    # Since "Contacts & Addresses" tab is injected, standard fields come first, meaning standard fields ARE in the Details tab.
    # Let's check which Custom Fields are currently after Contacts & Addresses.
    # The Contacts & Addresses tab is injected.
    
    # Let's see the order of fields now.
    doc = frappe.get_doc('DocType', 'Master Project')
    print("Standard fields:")
    for f in doc.fields:
        print(f"  {f.fieldname} ({f.fieldtype})")
        
    print("\nCustom fields:")
    cfs = frappe.get_all('Custom Field', filters={'dt': 'Master Project'}, fields=['name', 'fieldname', 'fieldtype', 'insert_after'])
    for cf in cfs:
        print(f"  {cf.fieldname} (after {cf.insert_after})")
        
    # We want Contacts & Addresses to come AFTER all the Details fields.
    # So Contacts & Addresses should be insert_after = 'tasks_html'.
    frappe.db.set_value('Custom Field', 'Master Project-custom_contacts__addresses', 'insert_after', 'tasks_html')
    frappe.db.commit()
    print("\nMoved Contacts & Addresses tab to be after 'tasks_html'.")

except Exception as e:
    print(f"Error: {e}")
finally:
    frappe.destroy()
