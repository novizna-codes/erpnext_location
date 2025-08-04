# Copyright (c) 2025, Your Company Name and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now


class Region(Document):
	def before_save(self):
		"""Update last_updated timestamp before saving"""
		self.last_updated = now()

	def validate(self):
		"""Validate Region data"""
		if not self.region_name:
			frappe.throw("Region Name is required")
		
		# Ensure region name is unique
		if self.is_new() or self.has_value_changed("region_name"):
			existing = frappe.db.exists("Region", {"region_name": self.region_name, "name": ["!=", self.name]})
			if existing:
				frappe.throw(f"Region with name '{self.region_name}' already exists")

	def after_insert(self):
		"""Actions after inserting a new region"""
		frappe.logger().info(f"New region created: {self.region_name}")

	@frappe.whitelist()
	def get_subregions(self):
		"""Get all subregions belonging to this region"""
		return frappe.get_all("Subregion", 
			filters={"region": self.name},
			fields=["name", "subregion_name", "wikidata_id"]
		)

	@frappe.whitelist() 
	def get_countries(self):
		"""Get all countries in this region"""
		return frappe.get_all("Country",
			filters={"region": self.region_name},
			fields=["name", "code", "iso3", "capital"]
		)
