# Copyright (c) 2026, Velmurugan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Equipment(Document):
	def on_submit(self):
		subcontracted = self.is_subcontracted
		if subcontracted == 1:
			doc = frappe.db.count("Equipment", self.name)
			frappe.db.set_value("Supplier", self.vendor, "total_subcontracts", doc)
		else:
			doc = frappe.db.count("Equipment", self.name)
			frappe.db.set_value("Vendor", self.vendor, "total_equipment_purchases", doc)

	def validate(self):
		if not self.daily_rate:
			self.daily_rate = self.get_daily_rate(self.equipment_category)

	def get_daily_rate(self, category):
		while True:
			daily_rate = frappe.db.get_value("Equipment Category", category, "daily_rental_rate")
			if daily_rate:
				return daily_rate
			category = frappe.db.get_value("Equipment Category", category, "parent_equipment_category")
			if not category:
				break
		return 0
