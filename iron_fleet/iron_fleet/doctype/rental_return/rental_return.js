// Copyright (c) 2026, Velmurugan and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Rental Return", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on("Rental Return", {
	setup(frm) {
		frm.set_query("rental_agreement", function () {
			return {
				filters: {
					docstatus: 1,
				},
			};
		});
	},
	refresh(frm) {
		frm.add_custom_button(__("Create Invoice"), function () {
			frappe.new_doc("Invoice", {
				equipment: frm.doc.equipment,
			});
		});
	},
	rental_agreement(frm) {
		if (frm.doc.rental_agreement) {
			frappe.call({
				method: "iron_fleet.iron_fleet.doctype.rental_return.rental_return.get_rental_agreement_details",
				args: {
					rental_agreement: frm.doc.rental_agreement,
				},
				callback: function (r) {
					if (r.message) {
						r.message.forEach(function (item) {
							let row = frm.add_child("return_item");
							row.equipment = item.equipments;
							frm.refresh_field("return_item");
						});
					}
				},
			});
		}
	},
});
