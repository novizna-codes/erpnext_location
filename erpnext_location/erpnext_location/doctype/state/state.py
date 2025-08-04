# Copyright (c) 2025, Novizna PVT LTD.
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class State(Document):
    def before_insert(self):
        """Set country code from country before insert"""
        if self.country and not self.country_code:
            country_doc = frappe.get_doc("Country", self.country)
            self.country_code = country_doc.code

    def before_save(self):
        """Update last_updated timestamp"""
        self.last_updated = frappe.utils.now()

    def validate(self):
        """Validate state data"""
        # Ensure country code matches the linked country
        if self.country:
            country_doc = frappe.get_doc("Country", self.country)
            if self.country_code and self.country_code != country_doc.code:
                frappe.throw(f"Country code mismatch. Expected {country_doc.code}, got {self.country_code}")
            self.country_code = country_doc.code
