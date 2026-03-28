# Copyright (c) 2026, Velmurugan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class EquipmentProcurement(Document):
	def on_submit(self):
		supplier_map = {}
		for row in self.procurement_details:
			if row.supplier not in supplier_map:
				supplier_map[row.supplier] = []
			supplier_map[row.supplier].append(row)
		for supplier, items in supplier_map.items():
			procurement_invoice = frappe.new_doc("Procurement Invoice")
			procurement_invoice.supplier = supplier
			procurement_invoice.equipment_procurement = self.name
			procurement_invoice.invoice_date = self.delivery_date
			procurement_invoice.is_subcontracted = self.is_subcontracted
			total = 0
			for row in items:
				procurement_invoice.append(
					"items",
					{
						"equipment_category": row.equipment_category,
						"quantity": row.quantity,
						"rate": row.rate,
						"total_price": row.total_price,
					},
				)
				total += row.total_price
			procurement_invoice.total_amount = total
			procurement_invoice.insert(ignore_permissions=True)
			# procurement_invoice.supplier = supplier
			# procurement_invoice.equipment_procurement = self.name
			# procurement_invoice.invoice_date = self.delivery_date
			# procurement_invoice.is_subcontracted = self.is_subcontracted
			# total = 0
			# for row in items:
			# 	procurement_invoice.append("items", {
			# 		"equipment_category": row.equipment_category,
			# 		"quantity": row.quantity,
			# 		"rate": row.rate,
			# 		"total_price": row.total_price
			# 	})
			# 	total += row.total_price
			# procurement_invoice.total_amount = total
			# procurement_invoice.insert(ignore_permissions=True)
