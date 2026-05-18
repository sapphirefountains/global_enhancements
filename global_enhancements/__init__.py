__version__ = "0.0.1"

import frappe
from global_enhancements.utils.patch_delete import patch_delete_doc

def monkey_patch():
	try:
		patch_delete_doc()
	except Exception:
		pass

# Run patch
monkey_patch()
