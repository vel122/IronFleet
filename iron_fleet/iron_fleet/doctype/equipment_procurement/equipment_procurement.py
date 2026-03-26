# Copyright (c) 2026, Velmurugan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class EquipmentProcurement(Document):
	pass


@frappe.whitelist()
def get_suppliers_by_category(doctype, txt, searchfield, start, page_len, filters):
	category = filters.get("equipment_category")

	return frappe.db.sql(
		"""
        SELECT DISTINCT s.name
        FROM `tabSupplier` s
        JOIN `tabSupplier Equipment Category` sec
        ON sec.parent = s.name
        WHERE sec.equipment_category = %s
        AND s.name LIKE %s
    """,
		(category, f"%{txt}%"),
	)
