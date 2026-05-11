import frappe
import json

def get_fields():
    fields = frappe.get_all('DocField', filters={'parent': 'Master Project'}, fields=['fieldname', 'label', 'fieldtype', 'idx'])
    print("Standard Fields:")
    print(json.dumps(fields, indent=2))
    
    custom_fields = frappe.get_all('Custom Field', filters={'dt': 'Master Project'}, fields=['fieldname', 'label', 'fieldtype', 'idx', 'insert_after'])
    print("\nCustom Fields:")
    print(json.dumps(custom_fields, indent=2))
