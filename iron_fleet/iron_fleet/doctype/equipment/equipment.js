// Copyright (c) 2026, Velmurugan and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Equipment", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on("Equipment", {
	refresh(frm) {
		if (frm.doc.next_maintanence_date) {
			let today = frappe.datetime.get_today();
			let nextMaintenanceDate = frm.doc.next_maintanence_date;
			let daysDifference = frappe.datetime.get_diff(nextMaintenanceDate, today);

			if (daysDifference <= 7 && daysDifference >= 0) {
				frappe.show_alert({
					message: __("Maintenance due in {0} days", [daysDifference]),
					indicator: "orange",
				});
			}
		}
	},
});
