# Copyright (c) 2026, Velmurugan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Equipment(Document):
	def get_category(category):
		while category:
			category = frappe.db.get_value(
				"Equipment Category",
				category,
				["daily_rental_rate", "parent_equipment_category"],
				as_dict=True,
			)
			if category.daily_rental_rate:
				return category.daily_rental_rate
			category = category.parent_equipment_category
		return category
