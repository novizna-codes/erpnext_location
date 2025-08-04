# Copyright (c) 2025, Novizna PVT LTD.
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class City(Document):
    def before_insert(self):
        """Set country and state codes before insert"""
        if self.state and not self.state_code:
            state_doc = frappe.get_doc("State", self.state)
            self.state_code = state_doc.state_code
            self.country = state_doc.country
            self.country_code = state_doc.country_code

    def before_save(self):
        """Update last_updated timestamp"""
        self.last_updated = frappe.utils.now()

    def validate(self):
        """Validate city data"""
        # Ensure state and country are linked correctly
        if self.state:
            state_doc = frappe.get_doc("State", self.state)
            if self.country and self.country != state_doc.country:
                frappe.throw(f"Country mismatch. State {self.state} belongs to {state_doc.country}, not {self.country}")

            # Auto-set country from state
            self.country = state_doc.country
            self.country_code = state_doc.country_code
            self.state_code = state_doc.state_code
