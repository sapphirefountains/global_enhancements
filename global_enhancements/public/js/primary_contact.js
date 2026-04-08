const primary_contact_doctypes = ['Project', 'Opportunity', 'Lead', 'Supplier', 'Customer'];

primary_contact_doctypes.forEach(doctype => {
	frappe.ui.form.on(doctype, {
		primary_contact: function(frm) {
			if (frm.doc.primary_contact) {
				// Fetch contact details
				frappe.db.get_value('Contact', frm.doc.primary_contact,
					['designation', 'phone', 'mobile_no', 'email_id'])
				.then(r => {
					if (r && r.message) {
						let values = r.message;
						frm.set_value('primary_contact_job_title', values.designation || '');
						frm.set_value('primary_contact_phone', values.phone || values.mobile_no || '');
						frm.set_value('primary_contact_email', values.email_id || '');
					}
				});
			} else {
				// Clear details if contact is removed
				frm.set_value('primary_contact_job_title', '');
				frm.set_value('primary_contact_phone', '');
				frm.set_value('primary_contact_email', '');
			}
		}
	});
});
