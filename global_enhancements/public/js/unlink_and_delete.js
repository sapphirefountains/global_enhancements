// Patches frappe.model.delete_doc globally to intercept link-exists errors (HTTP 417)
// and offer the user an "Unlink Document(s) and Delete" option.
(function () {
	const _original_delete_doc = frappe.model.delete_doc;

	frappe.model.delete_doc = function (doctype, name, callback) {
		frappe.call({
			method: "frappe.client.delete",
			args: { doctype, name },
			callback: function (r) {
				callback && callback(r);
			},
			error: function (r, http_status) {
				if (http_status === 417) {
					_show_unlink_dialog(doctype, name, r, callback);
				} else {
					// Not a link error — fall back to Frappe's default handler
					frappe.request.error({ method: "frappe.client.delete", args: { doctype, name } }, r, { status: http_status });
				}
			},
		});
	};

	function _parse_server_messages(r) {
		try {
			const msgs = JSON.parse(r._server_messages || "[]");
			return msgs
				.map((m) => {
					try {
						return JSON.parse(m).message || "";
					} catch (e) {
						return m || "";
					}
				})
				.join("");
		} catch (e) {
			return __("This document is linked with other documents and cannot be deleted.");
		}
	}

	function _show_unlink_dialog(doctype, name, r, callback) {
		const msg_html = _parse_server_messages(r);

		const d = new frappe.ui.Dialog({
			title: __("Cannot Delete — Document Has Links"),
			fields: [
				{
					fieldtype: "HTML",
					options: `<div style="max-height:320px;overflow-y:auto;padding:4px 0;">${msg_html}</div>`,
				},
			],
			primary_action_label: __("Unlink Document(s) and Delete"),
			primary_action() {
				d.hide();
				frappe.confirm(
					__(
						"This will remove all references to <b>{0} – {1}</b> from linked documents and then permanently delete it. Continue?",
						[doctype, name]
					),
					function () {
						frappe.call({
							method: "global_enhancements.delete_utils.unlink_and_delete",
							args: { doctype, name },
							freeze: true,
							freeze_message: __("Unlinking and deleting…"),
							callback(res) {
								if (res.message && res.message.success) {
									frappe.show_alert(
										{
											message: __("{0} has been deleted.", [name]),
											indicator: "green",
										},
										5
									);
									const route = frappe.get_route();
									if (
										route[0] === "Form" &&
										route[1] === doctype &&
										route[2] === name
									) {
										frappe.set_route("List", doctype);
									}
									callback && callback(res);
								}
							},
						});
					}
				);
			},
			secondary_action_label: __("Cancel"),
			secondary_action() {
				d.hide();
			},
		});

		d.show();
	}
})();
