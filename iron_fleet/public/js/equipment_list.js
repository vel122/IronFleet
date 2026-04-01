frappe.listview_settings["Equipment"] = {
	add_fields: [
		"status",
		"next_maintanence_date",
		"insurance_expiry_date",
		"registration_expiry_date",
	],
	get_indicator: function (doc) {
		if (doc.insurance_expiry_date) {
			let today = frappe.datetime.get_today();
			let insuranceExpiryDate = doc.insurance_expiry_date;
			let daysDifference = frappe.datetime.get_day_diff(insuranceExpiryDate, today);

			if (daysDifference <= 30 && daysDifference >= 0) {
				return ["Insurance Expired", "red", "insurance_expiry_date"];
			}
		}
		if (doc.registration_expiry_date) {
			let today = frappe.datetime.get_today();
			let registrationExpiryDate = doc.registration_expiry_date;
			let daysDifference = frappe.datetime.get_day_diff(registrationExpiryDate, today);

			if (daysDifference <= 30 && daysDifference >= 0) {
				return ["Registration Expired", "red", "registration_expiry_date"];
			}
		}
		if (doc.next_maintanence_date) {
			let today = frappe.datetime.get_today();
			let nextMaintenanceDate = doc.next_maintanence_date;
			let daysDifference = frappe.datetime.get_day_diff(nextMaintenanceDate, today);

			if (daysDifference <= 7 && daysDifference >= 0) {
				return ["Near Maintanence", "orange", "next_maintanence_date"];
			}
		}
		if (doc.status === "Rented") {
			return ["Rented", "blue", "status"];
		}
	},
};
