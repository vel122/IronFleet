# Copyright (c) 2026, Velmurugan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class RentalInvoice(Document):
	def on_submit(self):
		frappe.db.set_value("Rental Agreement", self.rental_agreement, "outstanding_amount", 0)
		frappe.db.set_value("Rental Agreement", self.rental_agreement, "payment_status", "Fully Paid")
