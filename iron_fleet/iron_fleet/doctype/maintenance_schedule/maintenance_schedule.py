# Copyright (c) 2026, Velmurugan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class MaintenanceSchedule(Document):
	def on_update(self):
		if self.status == "Completed":
			frappe.db.set_value("Equipment", self.equipment, "status", "Available")
