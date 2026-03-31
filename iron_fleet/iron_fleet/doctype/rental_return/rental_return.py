# Copyright (c) 2026, Velmurugan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import date_diff


class RentalReturn(Document):
	def validate(self):
		self.fetch_equipment()
		self.calculate_actual_days()
		self.calculate_late_fee()
		self.calculate_damage_fee()
		self.calculate_paid_amount()

	def fetch_equipment(self):
		if self.rental_agreement and not self.return_item:
			agreement = frappe.get_doc("Rental Agreement", self.rental_agreement)
			for item in agreement.rental_agreement_item:
				self.append("return_item", {"equipment": item.equipment})

	def calculate_actual_days(self):
		doc = frappe.db.get_value("Rental Agreement", self.rental_agreement, "rental_start_date")
		self.actual_rental_days = date_diff(self.return_date, doc)

	def calculate_late_fee(self):
		settings = frappe.get_cached_doc("Rental Settings")
		agreement = frappe.db.get_value("Rental Agreement", self.rental_agreement, "rental_start_date")
		late_days = date_diff(self.return_date, agreement)
		if late_days > 0:
			self.late_fee = (settings.late_fee_per_day or 0) * late_days
		else:
			self.late_fee = 0

	def calculate_damage_fee(self):
		total_damage_charges = 0
		for item in self.return_item:
			if item.damage_charge:
				total_damage_charges += item.damage_charge
		self.total_damage_charges = total_damage_charges

	def update_equipment_status(self):
		for item in self.return_item:
			if item.condition_on_return == "Damaged":
				frappe.get_doc(
					{
						"doctype": "Maintenance Schedule",
						"equipment": item.equipment,
						"maintenance_type": "Repair",
						"status": "Open",
					}
				).insert(ignore_permissions=True)
				frappe.db.set_value("Equipment", item.equipment, "status", "Under Maintenance")
			else:
				frappe.db.set_value("Equipment", item.equipment, "status", "Available")

	def calculate_paid_amount(self):
		paid_amount = 0
		doc = frappe.get_doc("Rental Agreement", self.rental_agreement)
		for item in doc.payment_schedule:
			paid_amount += item.amount_paid or 0
		self.outstanding_amount = doc.outstanding_amount
		self.paid_amount = paid_amount
		self.invoice_amount = (
			(doc.outstanding_amount or 0) + (self.late_fee or 0) + (self.total_damage_charges or 0)
		)

	def on_submit(self):
		self.update_equipment_status()
		frappe.enqueue(
			"iron_fleet.iron_fleet.doctype.rental_return.rental_return.create_rental_invoice",
			queue="default",
			name=self.name,
		)


@frappe.whitelist()
def get_rental_agreement_details(rental_agreement):
	return frappe.db.get_all(
		"Equipments Assigned", filters={"parent": rental_agreement}, fields=["equipments"]
	)


def create_rental_invoice(name):
	doc = frappe.get_doc("Rental Return", name)
	frappe.get_doc(
		{
			"doctype": "Rental Invoice",
			"rental_agreement": doc.rental_agreement,
			"invoice_amount": doc.invoice_amount,
		}
	).insert(ignore_permissions=True)
