# Copyright (c) 2025, Your Company Name and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now


class Subregion(Document):
    def before_save(self):
        """Update last_updated timestamp before saving"""
        self.last_updated = now()

    def validate(self):
        """Validate Subregion data"""
        if not self.subregion_name:
            frappe.throw("Subregion Name is required")
        
        if not self.region:
            frappe.throw("Region is required")
            
        # Ensure subregion name is unique
        if self.is_new() or self.has_value_changed("subregion_name"):
            existing = frappe.db.exists("Subregion", {
                "subregion_name": self.subregion_name, 
                "name": ["!=", self.name]
            })
            if existing:
                frappe.throw(f"Subregion with name '{self.subregion_name}' already exists")

    def after_insert(self):
        """Actions after inserting a new subregion"""
        frappe.logger().info(f"New subregion created: {self.subregion_name}")

    @frappe.whitelist()
    def get_countries(self):
        """Get all countries in this subregion"""
        return frappe.get_all("Country",
            filters={"subregion": self.subregion_name},
            fields=["name", "code", "iso3", "capital", "region"]
        )
