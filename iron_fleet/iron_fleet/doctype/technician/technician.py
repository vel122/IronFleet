# Copyright (c) 2026, Velmurugan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Technician(Document):
	def after_insert(self):
		frappe.enqueue(
			"iron_fleet.iron_fleet.doctype.technician.technician.create_user",
			technician=self.name,
			enqueue_after_commit=True,
		)


def create_user(technician):
	tech = frappe.get_doc("Technician", technician)
	doc = frappe.get_doc(
		{
			"doctype": "User",
			"email": tech.email,
			"first_name": tech.technician_name,
			"enabled": 1,
			"send_welcome_email": 1,
			"roles": [{"role": "Technician"}],
		}
	).insert(ignore_permissions=True)
	frappe.db.set_value("Technician", technician, "user", doc.name)
