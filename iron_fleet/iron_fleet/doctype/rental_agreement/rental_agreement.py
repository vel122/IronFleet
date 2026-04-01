# Copyright (c) 2026, Velmurugan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname


class RentalAgreement(Document):
	def autoname(self):
		self.name = make_autoname("RA-.YYYY.-.#####")

	def validate(self):
		self.calculate_total()
		self.check_equipment_availability()

	def on_update(self):
		self.notify_next_approver()

	def calculate_total(self):
		total = 0
		for item in self.rental_agreement_item:
			total += (item.quantity or 0) * (item.daily_rate or 0) * (self.estimated_rental_days or 0)
		self.estimated_total = total
		self.total_daily_rate = sum((item.daily_rate or 0) for item in self.rental_agreement_item)

		self.discount_amount = (self.discount_percentage or 0) * self.estimated_total / 100

		settings = frappe.get_cached_doc("Rental Settings")
		if settings.default_security_deposit_percentage:
			self.security_deposit = (
				settings.default_security_deposit_percentage / 100
			) * self.estimated_total

		self.grand_total = self.estimated_total - (self.discount_amount or 0) + (self.security_deposit or 0)

	def check_equipment_availability(self):
		for item in self.rental_agreement_item:
			if item.equipment:
				qty = item.quantity or 0
				equipment_status = frappe.db.get_all(
					"Equipment", {"equipment_category": item.equipment, "status": "Available"}, limit=qty
				)
				if qty > len(equipment_status):
					frappe.throw(
						f"Only {len(equipment_status)} units of Equipment {item.equipment} are available for rent."
					)

	def before_submit(self):
		self.outstanding_amount = self.grand_total

		self.check_availability()
		self.check_maintenance_availability()
		self.build_payment_schedule()

	def check_availability(self):
		for item in self.rental_agreement_item:
			equipments = frappe.get_all(
				"Equipment",
				filters={"equipment_category": item.equipment, "status": "Available"},
			)
			if len(equipments) < item.quantity:
				frappe.throw(
					f"Only {len(equipments)} units of Equipment {item.equipment} are available for rent."
				)
				return
			selected_equipments = equipments[: item.quantity]
			for eq in selected_equipments:
				frappe.db.set_value("Equipment", eq.name, "status", "Rented")
				self.append("equipments", {"equipments": eq.name})

	def check_maintenance_availability(self):
		for item in self.rental_agreement_item:
			equipments = frappe.get_all(
				"Equipment",
				filters={
					"equipment_category": item.equipment,
					"status": "Available",
					"next_maintanence_date": ["between", [self.rental_start_date, self.rental_end_date]],
				},
			)
			selected_equipments = equipments[: item.quantity]
			if len(selected_equipments) > 0:
				frappe.throw(
					f"{len(selected_equipments)} units of Equipment {item.equipment} are due for maintenance during the rental period"
				)
				return

	def on_cancel(self):
		self.notify_customer()
		for item in self.equipments:
			frappe.db.set_value("Equipment", item.equipments, "status", "Available")

		payments = frappe.get_all(
			"Rental Payment", filters={"rental_agreement": self.name}, fields=["name", "docstatus"]
		)
		for payment in payments:
			doc = frappe.get_doc("Rental Payment", payment.name)
			if doc.docstatus == 1:
				doc.cancel()
		doc = frappe.get_doc("Rental Agreement", self.name)
		for item in doc.equipments:
			return frappe.db.set_value("Equipment", item.equipments, "status", "Available")

		rental_return = frappe.get_doc("Rental Return", self.name)
		if rental_return.docstatus == 1:
			rental_return.cancel()
		if rental_return.return_item:
			for item in rental_return.return_item:
				if item.condition_on_return == "Damaged":
					frappe.db.set_value("Equipment", item.equipment, "status", "Under Maintanence")
				else:
					frappe.db.set_value("Equipment", item.equipment, "status", "Available")

		rental = frappe.get_doc("Rental Invoice", self.name)
		if rental.docstatus == 1:
			rental.cancel()

	def notify_customer(self):
		doc = frappe.db.get_value("Customer", self.customer, "email")
		if doc:
			frappe.sendmail(
				recipients=[doc],
				subject=f"Rental Agreement {self.name} Update",
				message=f"Dear {self.customer},\n\nYour Rental Agreement {self.name} has been Cancelled",
			)

	def build_payment_schedule(self):
		settings = frappe.get_cached_doc("Rental Settings")
		total_amount = self.grand_total or 0
		advance = (settings.advance_ or 0) * total_amount / 100
		mid = (settings.mid_ or 0) * total_amount / 100
		final = total_amount - (advance + mid)
		self.append(
			"payment_schedule",
			{
				"installment_type": "Advance",
				"due_date": self.rental_start_date,
				"amount_due": advance,
				"amount_paid": 0,
				"status": "Pending",
			},
		)
		self.append(
			"payment_schedule",
			{
				"installment_type": "Mid",
				"due_date": self.rental_start_date + (self.rental_end_date - self.rental_start_date) / 2,
				"amount_due": mid,
				"amount_paid": 0,
				"status": "Pending",
			},
		)
		self.append(
			"payment_schedule",
			{
				"installment_type": "Final",
				"due_date": self.rental_end_date,
				"amount_due": final,
				"amount_paid": 0,
				"status": "Pending",
			},
		)

	def on_submit(self):
		for item in self.payment_schedule:
			new = frappe.new_doc("Rental Payment")
			new.rental_agreement = self.name
			new.installment_type = item.installment_type
			new.due_date = item.due_date
			new.amount_due = item.amount_due
			new.amount_paid = item.amount_paid
			new.status = item.status
			new.insert(ignore_permissions=True)

	def notify_next_approver(self):
		role_map = {
			"Pending Review": "Operations Head",
			"Operations Approval": "Operations Head",
			"Finance Clearance": "Finance Manager",
		}

		next_role = role_map.get(self.workflow_state)

		if not next_role:
			return

		users = frappe.get_all("Has Role", filters={"role": next_role}, fields=["parent"])

		for user in users:
			email = frappe.db.get_value("User", user.parent, "email")

			frappe.get_doc(
				{
					"doctype": "Notification Log",
					"subject": f"Approval Required: {self.name}",
					"for_user": user.parent,
					"type": "Alert",
					"document_type": self.doctype,
					"document_name": self.name,
				}
			).insert(ignore_permissions=True)

			if email:
				frappe.sendmail(
					recipients=[email],
					subject=f"Approval Required: {self.name}",
					message=f"""
					Rental Agreement {self.name} requires your approval.<br>
					Customer: {self.customer}<br>
					Amount: {self.grand_total}
					""",
				)


def check_overdue_payments(self):
	for payment in self.payment_schedule:
		if payment.status != "Paid" and payment.due_date < frappe.utils.nowdate():
			payment.status = "Overdue"
		frappe.sendmail(
			recipients=self.customer_email,
			subject=f"Overdue Payment for Rental Agreement {self.name}",
			message=f"Dear {self.customer},\n\nYour payment for the {payment.installment_type} installment of Rental Agreement {self.name} is overdue.",
		)
	self.save()
