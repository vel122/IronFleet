// Copyright (c) 2026, Velmurugan and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Rental Agreement", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on("Rental Agreement Item", {
	quantity: function (frm, cdt, cdn) {
		frm.trigger("calculate_total", cdt, cdn);
	},
	// daily_rate: function (frm, cdt, cdn) {
	//     frm.trigger("calculate_total", cdt, cdn);
	// },
	calculate_total: function (frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		let quantity = row.quantity || 0;
		let daily_rate = row.daily_rate || 0;
		let estimated_rental_days = frm.doc.estimated_rental_days || 0;
		let total = quantity * daily_rate * estimated_rental_days;
		frappe.model.set_value(cdt, cdn, "total", total);
	},

	equipment: function (frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		if (row.equipment) {
			frappe.db.get_value("Equipment Rate", row.equipment, "daily_rate").then((doc) => {
				if (!doc.message) {
					frappe.msgprint("No Daily Rate found for the selected equipment.");
					return;
				}
				let daily_rate = doc.message.daily_rate || 0;
				frappe.model.set_value(cdt, cdn, "daily_rate", daily_rate).then((r) => {
					frm.trigger("calculate_total", cdt, cdn);
				});
			});
		}
	},
});

frappe.ui.form.on("Rental Agreement", {
	rental_start_date: function (frm) {
		calculate_days(frm);
	},
	rental_end_date: function (frm) {
		calculate_days(frm);
	},
	before_workflow_action: function (frm) {
		if (frm.selected_workflow_action === "Reject") {
			frappe.prompt(
				[
					{
						fieldname: "rejection_reason",
						label: "Rejection Reason",
						fieldtype: "Small Text",
						reqd: 1,
					},
				],
				function (values) {
					frm.set_value("rejection_reason", values.rejection_reason);

					frm.save().then(() => {
						frappe.workflow.do_action(frm, "Reject");
					});
				},
				"Enter Rejection Reason"
			);

			return false;
		}
	},
});

function calculate_days(frm) {
	let rental_start_date = frm.doc.rental_start_date;
	let rental_end_date = frm.doc.rental_end_date;
	if (rental_start_date && rental_end_date) {
		let estimated_rental_days = frappe.datetime.get_day_diff(
			rental_end_date,
			rental_start_date
		);
		frm.set_value("estimated_rental_days", estimated_rental_days);
		frm.refresh_field("estimated_rental_days");
	}
}

// function calculate_total(frm, cdt, cdn) {
//         let row = locals[cdt][cdn];
//         let quantity = row.quantity || 0;
//         let daily_rate = row.daily_rate || 0;
//         let estimated_rental_days = frm.doc.estimated_rental_days || 0;
//         let total = quantity * daily_rate * estimated_rental_days;
//         frappe.model.set_value(cdt, cdn, "total", total);
//         frm.refresh_field("total");
// }
