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
		const sources = this.get_all_party_sources();

		if (sources.length === 0) return;

		// Build a filter that matches any of our sources in Dynamic Link
		const contact_filters = [
			["Dynamic Link", "link_name", "in", sources.map(s => s.name)]
		];

		if (frm.fields_dict.primary_contact) {
			frm.set_query("primary_contact", () => {
				return {
					query: "global_enhancements.api.get_contact_query", // We'll need a backend query for complex Dynamic Link filtering
					filters: {
						sources: sources
					}
				};
			});
			
			// Fallback if custom query isn't ready: Simple name-based filter
			// But for Link fields, we usually need a custom query to filter by Dynamic Link child table
		}

		if (frm.fields_dict.primary_address) {
			frm.set_query("primary_address", () => {
				return {
					filters: [
						["Dynamic Link", "link_name", "in", sources.map(s => s.name)]
					]
				};
			});
		}
	},

	get_all_party_sources: function() {
		const frm = this.frm;
		let sources = [];

		// 1. Add the document itself (direct links)
		sources.push({ doctype: frm.doctype, name: frm.doc.name });

		// 2. Add standard party fields
		if (frm.doc.customer) sources.push({ doctype: 'Customer', name: frm.doc.customer });
		if (frm.doc.supplier) sources.push({ doctype: 'Supplier', name: frm.doc.supplier });
		if (frm.doc.party_name && frm.doc.party_type) {
			sources.push({ doctype: frm.doc.party_type, name: frm.doc.party_name });
		}

		// 3. Scan child tables for links to Customer/Supplier
		// This handles custom multi-party child tables
		(frm.meta.fields || []).forEach(f => {
			if (f.fieldtype === "Table" && frm.doc[f.fieldname]) {
				const grid_rows = frm.doc[f.fieldname];
				grid_rows.forEach(row => {
					// Check for common link field names in child tables
					if (row.customer) sources.push({ doctype: 'Customer', name: row.customer });
					if (row.supplier) sources.push({ doctype: 'Supplier', name: row.supplier });
					if (row.party_name && row.party_type) {
						sources.push({ doctype: row.party_type, name: row.party_name });
					}
				});
			}
		});

		// De-duplicate by name
		const unique_sources = [];
		const map = new Map();
		for (const item of sources) {
			if (item.name && !map.has(item.name)) {
				map.set(item.name, true);
				unique_sources.push(item);
			}
		}

		return unique_sources;
	},

	render_all: function() {
		this.render_contact_table();
		this.render_google_map();
	},

	setup_events: function() {
		const frm = this.frm;
		
		// Re-render if any link fields change
		frappe.ui.form.on(frm.doctype, {
			customer: (frm) => this.render_all(),
			supplier: (frm) => this.render_all(),
			party_name: (frm) => this.render_all(),
			primary_address: (frm) => this.render_google_map()
		});
	},

	render_contact_table: function() {
		const frm = this.frm;
		if (!frm.fields_dict.contact_list_html) return;

		const sources = this.get_all_party_sources();
		const wrapper = $(frm.fields_dict.contact_list_html.wrapper);
		wrapper.empty();

		if (sources.length === 0) {
			wrapper.html('<div class="alert alert-warning">No linked parties found to display contacts.</div>');
			return;
		}

		wrapper.html('<div class="text-muted">Fetching aggregated contacts...</div>');

		// Add "Create New" buttons
		const btn_container = $('<div style="margin-bottom: 10px; display: flex; gap: 10px;"></div>').appendTo(wrapper);
		
		// Create button for the main entity or project
		$('<button class="btn btn-sm btn-default">Add Direct Contact</button>')
			.appendTo(btn_container)
			.on('click', () => this.create_new_contact(frm.doctype, frm.doc.name));

		// If it's a project with a customer, add button for customer too
		if (frm.doc.customer) {
			$(`<button class="btn btn-sm btn-default">Add Contact to ${frm.doc.customer}</button>`)
				.appendTo(btn_container)
				.on('click', () => this.create_new_contact('Customer', frm.doc.customer));
		}

		frappe.call({
			method: "frappe.client.get_list",
			args: {
				doctype: "Contact",
				filters: [
					["Dynamic Link", "link_name", "in", sources.map(s => s.name)]
				],
				fields: ["name", "first_name", "last_name", "custom_title", "custom_phone_number", "custom_mobile_number", "custom_email", "is_primary_contact"]
			},
			callback: (r) => {
				wrapper.find('.text-muted').remove();
				if (!r.message || r.message.length === 0) {
					wrapper.append('<div class="alert alert-warning">No contacts linked to any related parties yet.</div>');
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
								<button class="btn btn-xs btn-primary set-primary-contact" data-name="${c.name}" style="margin-left: 5px;">
									Set Primary
								</button>
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
		// When setting primary in a multi-party context, we uncheck others linked to the current document's primary party
		// For simplicity, we'll use the main party field if available
		const main_party_name = frm.doc.customer || frm.doc.supplier || frm.doc.party_name || frm.doc.name;
		const main_party_doctype = frm.doc.customer ? 'Customer' : (frm.doc.supplier ? 'Supplier' : (frm.doc.party_type || frm.doctype));

		frappe.confirm(`Set ${contact_name} as primary for ${main_party_name}?`, () => {
			frappe.call({
				method: "global_enhancements.sync_contact.set_primary_contact",
				args: {
					account_doctype: main_party_doctype,
					account_name: main_party_name,
					contact_name: contact_name
				},
				callback: (r) => {
					frm.set_value('primary_contact', contact_name);
					frm.save().done(() => {
						this.render_contact_table();
						frappe.show_alert({message: __("Primary contact updated"), indicator: "green"});
					});
				}
			});
		});
	},

	create_new_contact: function(link_doctype, link_name) {
		frappe.route_options = {
			"links": [{ "link_doctype": link_doctype, "link_name": link_name }]
		};
		frappe.ui.form.make_quick_entry('Contact', (doc) => {
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
			args: { doctype: "Address", name: address_name },
			callback: (r) => {
				wrapper.find('.text-muted').remove();
				if (r.message) {
					const addr = r.message;
					const full_address = [addr.address_line1, addr.address_line2, addr.city, addr.state, addr.pincode, addr.country]
						.filter(Boolean).join(", ");
					const encoded_address = encodeURIComponent(full_address);
					wrapper.append(`
						<div style="width: 100%; height: 400px;">
							<iframe width="100%" height="100%" frameborder="0" style="border:0" 
								src="https://maps.google.com/maps?q=${encoded_address}&output=embed" allowfullscreen>
							</iframe>
						</div>
					`);
				}
			}
		});
	},

	create_new_address: function() {
		const frm = this.frm;
		const sources = this.get_all_party_sources();
		// Default to the first non-Project source if possible
		const target = sources.find(s => s.doctype !== frm.doctype) || sources[0];

		frappe.route_options = {
			"links": [{ "link_doctype": target.doctype, "link_name": target.name }]
		};

		frappe.ui.form.make_quick_entry('Address', (doc) => {
			frm.set_value('primary_address', doc.name);
			this.render_google_map();
		});
	}
};
