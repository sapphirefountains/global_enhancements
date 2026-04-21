frappe.provide("global_enhancements.unified_controller");

frappe.ui.form.on('Customer', { refresh: (frm) => global_enhancements.unified_controller.init(frm) });
frappe.ui.form.on('Supplier', { refresh: (frm) => global_enhancements.unified_controller.init(frm) });
frappe.ui.form.on('Opportunity', { refresh: (frm) => global_enhancements.unified_controller.init(frm) });
frappe.ui.form.on('Project', { refresh: (frm) => global_enhancements.unified_controller.init(frm) });
frappe.ui.form.on('Contact', { refresh: (frm) => global_enhancements.unified_controller.init(frm) });

global_enhancements.unified_controller = {
	init: function(frm) {
		this.frm = frm;
		this.setup_queries();
		this.render_all();
		this.setup_events();
	},

	setup_queries: function() {
		const frm = this.frm;
		const account = this.get_account_context();

		if (!account) return;

		if (frm.fields_dict.primary_contact) {
			frm.set_query("primary_contact", () => {
				return {
					filters: [
						["Dynamic Link", "link_doctype", "=", frm.doctype === "Opportunity" ? "Customer" : frm.doctype],
						["Dynamic Link", "link_name", "=", account]
					]
				};
			});
		}

		if (frm.fields_dict.primary_address) {
			frm.set_query("primary_address", () => {
				return {
					filters: [
						["Dynamic Link", "link_doctype", "=", frm.doctype === "Opportunity" ? "Customer" : (frm.doctype === "Contact" ? "Contact" : frm.doctype)],
						["Dynamic Link", "link_name", "=", account]
					]
				};
			});
		}
	},

	get_account_context: function() {
		const frm = this.frm;
		if (frm.doctype === "Customer" || frm.doctype === "Supplier" || frm.doctype === "Contact") {
			return frm.doc.name;
		} else if (frm.doctype === "Opportunity") {
			return frm.doc.party_name;
		} else if (frm.doctype === "Project") {
			return frm.doc.customer;
		}
		return null;
	},

	get_link_doctype: function() {
		const frm = this.frm;
		if (frm.doctype === "Opportunity") return "Customer";
		return frm.doctype;
	},

	render_all: function() {
		this.render_contact_table();
		this.render_google_map();
	},

	setup_events: function() {
		const frm = this.frm;
		// Trigger on account change if applicable
		const account_field = this.get_account_field();
		if (account_field) {
			frappe.ui.form.on(frm.doctype, account_field, (frm) => {
				this.setup_queries();
				this.render_all();
			});
		}

		// Trigger map on address change
		if (frm.fields_dict.primary_address) {
			frappe.ui.form.on(frm.doctype, "primary_address", (frm) => {
				this.render_google_map();
			});
		}
	},

	get_account_field: function() {
		const frm = this.frm;
		if (frm.doctype === "Opportunity") return "party_name";
		if (frm.doctype === "Project") return "customer";
		return null;
	},

	render_contact_table: function() {
		const frm = this.frm;
		if (!frm.fields_dict.contact_list_html) return;

		const account = this.get_account_context();
		const wrapper = $(frm.fields_dict.contact_list_html.wrapper);
		wrapper.empty();

		if (!account) {
			wrapper.html('<div class="alert alert-warning">Please select an account to view contacts.</div>');
			return;
		}

		wrapper.html('<div class="text-muted">Fetching contacts...</div>');

		// Add "Create New Contact" button
		const btn_container = $('<div style="margin-bottom: 10px;"></div>').appendTo(wrapper);
		$('<button class="btn btn-sm btn-default">Create New Contact</button>')
			.appendTo(btn_container)
			.on('click', () => this.create_new_contact());

		frappe.call({
			method: "frappe.client.get_list",
			args: {
				doctype: "Contact",
				filters: [
					["Dynamic Link", "link_doctype", "=", this.get_link_doctype()],
					["Dynamic Link", "link_name", "=", account]
				],
				fields: ["name", "first_name", "last_name", "custom_title", "custom_phone_number", "custom_mobile_number", "custom_email", "is_primary_contact"]
			},
			callback: (r) => {
				wrapper.find('.text-muted').remove();
				if (!r.message || r.message.length === 0) {
					wrapper.append('<div class="alert alert-warning">No contacts linked to this account yet.</div>');
					return;
				}

				let table = `
					<table class="table table-bordered table-hover" style="background: white;">
						<thead>
							<tr>
								<th>Name</th>
								<th>Title</th>
								<th>Email</th>
								<th>Phone</th>
								<th>Actions</th>
							</tr>
						</thead>
						<tbody>
				`;

				r.message.forEach(c => {
					const full_name = [c.first_name, c.last_name].filter(Boolean).join(" ") || c.name;
					const phone = c.custom_phone_number || c.custom_mobile_number || "";
					const is_primary = c.is_primary_contact ? '<span class="label label-primary" style="margin-left: 5px;">Primary</span>' : '';
					
					table += `
						<tr data-name="${c.name}">
							<td>${full_name}${is_primary}</td>
							<td>${c.custom_title || ""}</td>
							<td>${c.custom_email || ""}</td>
							<td>${phone}</td>
							<td>
								<button class="btn btn-xs btn-default edit-contact" data-name="${c.name}" title="Edit">
									<i class="fa fa-pencil"></i>
								</button>
								${!c.is_primary_contact ? `
								<button class="btn btn-xs btn-primary set-primary-contact" data-name="${c.name}" style="margin-left: 5px;">
									Set Primary
								</button>` : ''}
							</td>
						</tr>
					`;
				});

				table += '</tbody></table>';
				wrapper.append(table);

				wrapper.find('.edit-contact').on('click', (e) => {
					const name = $(e.currentTarget).data('name');
					window.open(frappe.urllib.get_full_url(`/app/contact/${name}`), '_blank');
				});

				wrapper.find('.set-primary-contact').on('click', (e) => {
					const name = $(e.currentTarget).data('name');
					this.set_primary_contact(name);
				});
			}
		});
	},

	set_primary_contact: function(contact_name) {
		const frm = this.frm;
		const account = this.get_account_context();
		const link_doctype = this.get_link_doctype();

		frappe.confirm(`Are you sure you want to set ${contact_name} as the primary contact?`, () => {
			frappe.call({
				method: "frappe.client.get_list",
				args: {
					doctype: "Contact",
					filters: [
						["Dynamic Link", "link_doctype", "=", link_doctype],
						["Dynamic Link", "link_name", "=", account],
						["is_primary_contact", "=", 1]
					],
					fields: ["name"]
				},
				callback: (r) => {
					const promises = [];
					if (r.message) {
						r.message.forEach(old_primary => {
							promises.push(frappe.db.set_value('Contact', old_primary.name, 'is_primary_contact', 0));
						});
					}

					$.when(...promises).done(() => {
						frappe.db.set_value('Contact', contact_name, 'is_primary_contact', 1).done(() => {
							frm.set_value('primary_contact', contact_name);
							frm.save().done(() => {
								this.render_contact_table();
								frappe.show_alert({message: __("Primary contact updated"), indicator: "green"});
							});
						});
					});
				}
			});
		});
	},

	create_new_contact: function() {
		const frm = this.frm;
		const account = this.get_account_context();
		const link_doctype = this.get_link_doctype();

		frappe.new_doc('Contact', {
			links: [
				{
					link_doctype: link_doctype,
					link_name: account
				}
			]
		}, (doc) => {
			this.render_contact_table();
		});
	},

	render_google_map: function() {
		const frm = this.frm;
		if (!frm.fields_dict.location_map_html) return;

		const wrapper = $(frm.fields_dict.location_map_html.wrapper);
		wrapper.empty();

		// Add "Create New Address" button
		const btn_container = $('<div style="margin-bottom: 10px;"></div>').appendTo(wrapper);
		$('<button class="btn btn-sm btn-default">Create New Address</button>')
			.appendTo(btn_container)
			.on('click', () => this.create_new_address());

		const address_name = frm.doc.primary_address;

		if (!address_name) {
			wrapper.append('<div class="alert alert-secondary">Select a Primary Address to view the map.</div>');
			return;
		}

		wrapper.append('<div class="text-muted">Loading map...</div>');

		frappe.call({
			method: "frappe.client.get",
			args: {
				doctype: "Address",
				name: address_name
			},
			callback: (r) => {
				wrapper.find('.text-muted').remove();
				if (r.message) {
					const addr = r.message;
					const full_address = [addr.address_line1, addr.address_line2, addr.city, addr.state, addr.pincode, addr.country]
						.filter(Boolean).join(", ");
					
					const encoded_address = encodeURIComponent(full_address);
					const iframe = `
						<div style="width: 100%; height: 400px;">
							<iframe 
								width="100%" 
								height="100%" 
								frameborder="0" 
								style="border:0" 
								src="https://www.google.com/maps?q=${encoded_address}&output=embed" 
								allowfullscreen>
							</iframe>
						</div>
					`;
					wrapper.append(iframe);
				}
			}
		});
	},

	create_new_address: function() {
		const frm = this.frm;
		const account = this.get_account_context();
		const link_doctype = (frm.doctype === "Contact") ? "Contact" : this.get_link_doctype();

		frappe.new_doc('Address', {
			links: [
				{
					link_doctype: link_doctype,
					link_name: account
				}
			]
		}, (doc) => {
			frm.set_value('primary_address', doc.name);
			this.render_google_map();
		});
	}
};
