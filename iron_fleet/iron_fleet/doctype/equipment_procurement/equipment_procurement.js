// Copyright (c) 2026, Velmurugan and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Equipment Procurement", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on("Equipment Procurement", {
	refresh: function (frm) {
		frm.fields_dict["procurement_details"].grid.get_field("supplier").get_query = function (
			doc,
			cdt,
			cdn
		) {
			let row = locals[cdt][cdn];

			return {
				filters: {
					"equipment_category.equipment_category": row.equipment_category,
				},
			};
		};
	},
});
frappe.ui.form.on("Procurement Details", {
	quantity: function (frm, cdt, cdn) {
		calculate_total(frm, cdt, cdn);
	},
	rate: function (frm, cdt, cdn) {
		calculate_total(frm, cdt, cdn);
	},
});

function calculate_total(frm, cdt, cdn) {
	let row = locals[cdt][cdn];
	let quantity = row.quantity || 0;
	let rate = row.rate || 0;
	let total_price = quantity * rate;
	frappe.model.set_value(cdt, cdn, "total_price", total_price);
	frm.refresh_field("total_price");
}
