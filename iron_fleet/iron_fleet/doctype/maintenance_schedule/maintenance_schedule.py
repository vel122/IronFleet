# Copyright (c) 2026, Velmurugan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import add_days, today


class MaintenanceSchedule(Document):
	def validate(self):
		self.calculate_cost()
		self.reduce_quantity()
		self.check_technician()

	def calculate_cost(self):
		self.total_cost = sum(item.total for item in self.parts_used) + (self.labor_cost or 0)

	def reduce_quantity(self):
		for p in self.parts_used:
			if not p.part_name:
				continue
			doc = frappe.db.get_value("Spare Parts", p.part_name, "quantity")
			if p.quantity > doc:
				frappe.throw(
					f"Not enough quantity for part {p.part_name}. Available: {doc}, Required: {p.quantity}"
				)
			qty = doc - p.quantity
			frappe.db.set_value("Spare Parts", p.part_name, "quantity", qty)

	def check_technician(self):
		if self.workflow_state == "Assigned" and not self.assigned_technician:
			frappe.throw("Please assign a technician before proceeding.")

	def on_update(self):
		if self.workflow_state == "Verified":
			doc = frappe.get_cached_doc("Rental Settings")
			frappe.db.set_value(
				"Equipment",
				self.equipment,
				{
					"status": "Available",
					"next_maintanence_date": add_days(today(), doc.maintanence_interval_days),
				},
			)


def create_maintenance_schedule():
	doc = frappe.get_all("Equipment", filters={"next_maintanence_date": today()}, fields=["name"])
	for equipment in doc:
		frappe.get_doc(
			{"doctype": "Maintenance Schedule", "equipment": equipment.name, "maintenance_type": "Preventive"}
		).insert(ignore_permissions=True)
