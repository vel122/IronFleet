# Copyright (c) 2026, Velmurugan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class RentalSettings(Document):
	def on_update(self):
		frappe.cache().delete("rental_settings")

	def rental_settings(self):
		cache = frappe.cache()
		key = "rental_settings"
		settings = cache.get(key)
		if settings:
			return settings
		settings = frappe.get_single("Rental Settings")
		cache.set(key, settings, expires_in_sec=3600)
		return settings
