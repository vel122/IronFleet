# Copyright (c) 2026, Velmurugan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class RentalPayment(Document):
	def on_submit(self):
		doc = frappe.get_doc("Rental Agreement", self.rental_agreement)
		for item in doc.payment_schedule:
			if item.installment_type == self.installment_type:
				item.amount_paid = self.amount_paid
				item.payment_mode = self.payment_mode
				item.reference_number = self.reference_number
				if item.amount_paid >= item.amount_due:
					item.status = "Paid"
				else:
					item.status = "Pending"
		doc.outstanding_amount = doc.grand_total - sum(item.amount_paid for item in doc.payment_schedule)
		if doc.outstanding_amount <= 0:
			doc.payment_status = "Fully Paid"
		elif doc.outstanding_amount < doc.grand_total:
			doc.payment_status = "Partially Paid"
		else:
			doc.payment_status = "Unpaid"
		doc.save()
