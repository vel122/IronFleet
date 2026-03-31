# Copyright (c) 2026, Velmurugan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import add_days, nowdate, random_string

from iron_fleet.iron_fleet.doctype.equipment.equipment import Equipment


class ProcurementPayment(Document):
	def on_submit(self):
		frappe.db.set_value("Procurement Invoice", self.invoice, "status", "Paid")
		qty = sum(item.quantity for item in self.payment_details)
		if self.is_subcontracted == 1:
			frappe.db.set_value("Supplier", self.supplier, "total_equipment_purchases", qty)
		else:
			frappe.db.set_value("Supplier", self.supplier, "total_subcontracts", qty)
		for row in self.payment_details:
			for _i in range(row.quantity):
				equipment = frappe.new_doc("Equipment")
				equipment.equipment_category = row.equipment_category
				equipment.status = "Available"
				equipment.condition_rating = "Excellent"
				equipment.maintanence_days = 7
				equipment.next_maintanence_date = add_days(nowdate(), 15)
				equipment.insurance_expiry_date = add_days(nowdate(), 365)
				equipment.registration_expiry_date = add_days(nowdate(), 730)
				equipment.location = "WH-Chennai"
				equipment.is_subcontracted = self.is_subcontracted
				equipment.daily_rate = Equipment.get_category(row.equipment_category)
				equipment.company = frappe.get_cached_doc("Rental Settings").company_name
				equipment.serial_no = (
					f"{self.supplier[:3].upper()}-{self.invoice[-4:].upper()}-{random_string(5).upper()}"
				)
				equipment.insert(ignore_permissions=True)

		new = frappe.new_doc("Equipment Rate")
		new.equipment_category = row.equipment_category
		new.daily_rate = Equipment.get_category(row.equipment_category)
		new.insert(ignore_permissions=True)
