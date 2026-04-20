const primary_contact_doctypes = ['Project', 'Opportunity', 'Lead', 'Supplier', 'Account'];

primary_contact_doctypes.forEach(doctype => {
	frappe.ui.form.on(doctype, {
		refresh: function(frm) {
			if (frappe.contacts && frappe.contacts.setup) {
				frappe.contacts.setup(frm);
			}

			// Call standard render so standard fields work
			if (frappe.contacts && frappe.contacts.render_address_and_contact) {
				frappe.contacts.render_address_and_contact(frm);
			}

			// Now render our custom bottom field
			render_enhanced_address_and_contact(frm);
		},
		primary_contact: function(frm) {
			if (frm.doc.primary_contact) {
				// Fetch contact details
				frappe.db.get_value('Contact', frm.doc.primary_contact,
					['custom_title', 'phone', 'mobile_no', 'custom_email'])
				.then(r => {
					if (r && r.message) {
						let values = r.message;
						frm.set_value('primary_contact_job_title', values.custom_title || '');
						frm.set_value('primary_contact_phone', values.phone || values.mobile_no || '');
						frm.set_value('primary_contact_email', values.custom_email || '');
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

function render_enhanced_address_and_contact(frm) {
	const field_wrapper = frm.fields_dict['custom_address_and_contact_html']?.wrapper;
	if (!field_wrapper) return;

	const $wrapper = $(field_wrapper);
	$wrapper.empty();

	const addr_list = frm.doc.__onload ? frm.doc.__onload.addr_list || [] : [];
	const contact_list = frm.doc.__onload ? frm.doc.__onload.contact_list || [] : [];

	let html = `
		<div class="row">
			<div class="col-md-6">
				<h4>${__('Addresses')}</h4>
				<p>
					<button class="btn btn-xs btn-default btn-new-custom-address" style="margin-right: 4px;">
						${__("New Address")}
					</button>
					<button class="btn btn-xs btn-default btn-add-existing-address">
						${__("Select Existing Address")}
					</button>
				</p>
				<div class="clearfix"></div>
				<div class="custom-address-list"></div>
			</div>
			<div class="col-md-6">
				<h4>${__('Contacts')}</h4>
				<p>
					<button class="btn btn-xs btn-default btn-new-custom-contact" style="margin-right: 4px;">
						${__("New Contact")}
					</button>
					<button class="btn btn-xs btn-default btn-add-existing-contact">
						${__("Select Existing Contact")}
					</button>
				</p>
				<div class="clearfix"></div>
				<div class="custom-contact-list"></div>
			</div>
		</div>
	`;

	$wrapper.html(html);

	const $address_list = $wrapper.find('.custom-address-list');
	if (addr_list.length === 0) {
		$address_list.append(`<p class="text-muted small">${__("No address added yet.")}</p>`);
	} else {
		addr_list.forEach(addr => {
			let addr_html = `
				<div class="address-box" style="position: relative; border: 1px solid #d1d8dd; padding: 10px; margin-bottom: 10px; border-radius: 4px;">
					<div class="edit-btn-container" style="position: absolute; right: 10px; top: 10px; display: flex; gap: 4px;">
						<a href="${frappe.utils.get_form_link('Address', addr.name)}" class="btn btn-xs btn-default edit-btn" title="${__('Edit')}">
							<svg class="icon icon-xs"><use href="#icon-edit"></use></svg>
						</a>
						<button class="btn btn-xs btn-default btn-remove-address" data-name="${addr.name}" title="${__('Remove Link')}">
							<svg class="icon icon-xs"><use href="#icon-trash"></use></svg>
						</button>
					</div>
					<p class="h6 flex flex-wrap">
						<span>${addr.address_title}</span>
						${addr.address_type !== "Other" ? `&nbsp;&#183;&nbsp;<span class="text-muted">${__(addr.address_type)}</span>` : ''}
						${addr.is_primary_address ? `&nbsp;&#183;&nbsp;<span class="text-muted">${__("Primary Address")}</span>` : ''}
						${addr.is_shipping_address ? `&nbsp;&#183;&nbsp;<span class="text-muted">${__("Shipping Address")}</span>` : ''}
						${addr.disabled ? `&nbsp;&#183;&nbsp;<span class="text-muted">${__("Disabled")}</span>` : ''}
					</p>
					<p>${addr.display}</p>
				</div>
			`;
			$address_list.append(addr_html);
		});
	}

	const $contact_list = $wrapper.find('.custom-contact-list');
	if (contact_list.length === 0) {
		$contact_list.append(`<p class="text-muted small">${__("No contacts added yet.")}</p>`);
	} else {
		contact_list.forEach(contact => {
			let contact_html = `
				<div class="contact-box" style="position: relative; border: 1px solid #d1d8dd; padding: 10px; margin-bottom: 10px; border-radius: 4px;">
					<div class="edit-btn-container" style="position: absolute; right: 10px; top: 10px; display: flex; gap: 4px;">
						<a href="${frappe.utils.get_form_link('Contact', contact.name)}" class="btn btn-xs btn-default edit-btn" title="${__('Edit')}">
							<svg class="icon icon-xs"><use href="#icon-edit"></use></svg>
						</a>
						<button class="btn btn-xs btn-default btn-remove-contact" data-name="${contact.name}" title="${__('Remove Link')}">
							<svg class="icon icon-xs"><use href="#icon-trash"></use></svg>
						</button>
					</div>
					<p class="h6 flex flex-wrap">
						<span>${contact.first_name || ''} ${contact.last_name || ''}</span>
						${contact.is_primary_contact ? `&nbsp;&#183;&nbsp;<span class="text-muted">${__("Primary Contact")}</span>` : ''}
						${contact.is_billing_contact ? `&nbsp;&#183;&nbsp;<span class="text-muted">${__("Billing Contact")}</span>` : ''}
						${contact.designation ? `&nbsp;&#183;&nbsp;<span class="text-muted">${contact.designation}</span>` : ''}
					</p>
					${contact.phone ? `<p><a href="tel:${frappe.utils.escape_html(contact.phone)}">${frappe.utils.escape_html(contact.phone)}</a> &#183; <span class="text-muted">${__("Primary Phone")}</span></p>` : ''}
					${contact.email_id ? `<p><a href="mailto:${frappe.utils.escape_html(contact.email_id)}">${frappe.utils.escape_html(contact.email_id)}</a> &#183; <span class="text-muted">${__("Primary Email")}</span></p>` : ''}
					${contact.address ? `<p>${contact.address}</p>` : ''}
				</div>
			`;
			$contact_list.append(contact_html);
		});
	}

	// Handlers for Select Existing
	$wrapper.find('.btn-add-existing-address').on('click', () => show_select_dialog('Address', frm));
	$wrapper.find('.btn-add-existing-contact').on('click', () => show_select_dialog('Contact', frm));

	// Handlers for New
	$wrapper.find('.btn-new-custom-address').on('click', () => new_record('Address', frm));
	$wrapper.find('.btn-new-custom-contact').on('click', () => new_record('Contact', frm));

	// Handlers for Remove
	$wrapper.find('.btn-remove-address').on('click', function() {
		remove_link('Address', $(this).data('name'), frm);
	});
	$wrapper.find('.btn-remove-contact').on('click', function() {
		remove_link('Contact', $(this).data('name'), frm);
	});
}

function show_select_dialog(doctype, frm) {
	const d = new frappe.ui.Dialog({
		title: __('Select Existing {0}', [__(doctype)]),
		fields: [
			{
				label: __(doctype),
				fieldname: 'docname',
				fieldtype: 'Link',
				options: doctype,
				reqd: 1
			}
		],
		primary_action_label: __('Add'),
		primary_action(values) {
			frappe.call({
				method: 'global_enhancements.api.add_link',
				args: {
					link_doctype: frm.doctype,
					link_name: frm.doc.name,
					doctype: doctype,
					name: values.docname
				},
				callback: function() {
					d.hide();
					frm.reload_doc();
				}
			});
		}
	});
	d.show();
}

function remove_link(doctype, name, frm) {
	frappe.confirm(__('Are you sure you want to remove this {0}?', [__(doctype)]), () => {
		frappe.call({
			method: 'global_enhancements.api.remove_link',
			args: {
				link_doctype: frm.doctype,
				link_name: frm.doc.name,
				doctype: doctype,
				name: name
			},
			callback: function() {
				frm.reload_doc();
			}
		});
	});
}

function new_record(doctype, frm) {
	frappe.dynamic_link = {
		doctype: frm.doc.doctype,
		doc: frm.doc,
		fieldname: "name",
	};

	if (frappe.boot.enable_address_autocompletion === 1 && doctype === "Address") {
		new frappe.ui.AddressAutocompleteDialog({
			title: __("New Address"),
			link_doctype: frm.doc.doctype,
			link_name: frm.doc.name,
			after_insert: function (doc) {
				frm.reload_doc();
			},
		}).show();
	} else {
		frappe.new_doc(doctype);
	}
}

