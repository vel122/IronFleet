// Copyright (c) 2026, Velmurugan and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Maintenance Schedule", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on("Maintenance Schedule", {
	setup(frm) {
		frm.set_query("assigned_technician", function () {
			return {
				filters: {
					status: "Active",
				},
			};
		});
	},
});

frappe.ui.form.on("Maintanence Part", {
	quantity(frm, cdt, cdn) {
		calculate_total(frm, cdt, cdn);
	},
	unit_cost(frm, cdt, cdn) {
		calculate_total(frm, cdt, cdn);
	},
});

function calculate_total(frm, cdt, cdn) {
	let row = locals[cdt][cdn];
	row.total = (row.quantity || 0) * (row.unit_cost || 0);

	frm.refresh_field("parts_used");
}
