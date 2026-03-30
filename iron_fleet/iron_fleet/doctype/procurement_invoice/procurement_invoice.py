# Copyright (c) 2026, Velmurugan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ProcurementInvoice(Document):
	def on_submit(self):
		frappe.db.set_value("Procurement Invoice", self.name, "status", "Draft")
		procurement_payment = frappe.new_doc("Procurement Payment")
		procurement_payment.invoice = self.name
		procurement_payment.supplier = self.supplier
		procurement_payment.total_amount = self.total_amount
		procurement_payment.is_subcontracted = self.is_subcontracted
		for row in self.items:
			procurement_payment.append(
				"payment_details",
				{
					"equipment_category": row.equipment_category,
					"quantity": row.quantity,
					"rate": row.rate,
					"total_price": row.total_price,
				},
			)
		procurement_payment.insert(ignore_permissions=True)
