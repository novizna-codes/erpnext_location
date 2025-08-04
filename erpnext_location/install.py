# Copyright (c) 2025, Novizna PVT LTD.
# MIT License

import frappe
from erpnext_location.erpnext_location.utils.data_import import refresh_location_data


def install_custom_fields():
    """Install custom fields for Country doctype"""
    try:
        # Import Country customization from ERPNext Location module
        frappe.reload_doc("erpnext_location", "doctype", "country", force=True)
        frappe.logger().info("Country customization imported successfully")
    except Exception as e:
        frappe.logger().error(f"Error importing Country customization: {str(e)}")
        # Try alternative method - direct file import
        try:
            import os
            import json

            # Path to customization file
            customization_path = os.path.join(
                frappe.get_app_path("erpnext_location"),
                "erpnext_location", "erpnext_location", "country.json"
            )

            if os.path.exists(customization_path):
                with open(customization_path, 'r') as f:
                    customizations = json.load(f)

                # Import customizations
                from frappe.core.doctype.data_import.data_import import import_doc
                for customization in customizations:
                    if customization.get("custom_fields"):
                        for field_data in customization["custom_fields"]:
                            if not frappe.db.exists("Custom Field", field_data["name"]):
                                field_doc = frappe.get_doc(field_data)
                                field_doc.insert(ignore_permissions=True)

                frappe.logger().info("Custom fields imported via direct method")
            else:
                frappe.logger().error(f"Customization file not found: {customization_path}")

        except Exception as e2:
            frappe.logger().error(f"Alternative import method also failed: {str(e2)}")

    frappe.db.commit()


def after_install():
    """Execute after app installation"""
    frappe.logger().info("Erpnext Location app installed successfully")

    # Import sample data during installation
    try:
        imported_count = refresh_location_data()
        frappe.logger().info(f"Imported {imported_count} sample countries during installation")

        # Show success message
        frappe.msgprint(
            f"Erpnext Location app installed successfully!<br>"
            f"<br>To import full dataset, go to:<br>",
            title="Installation Complete",
            indicator="green"
        )

    except Exception as e:
        frappe.logger().error(f"Error during installation: {str(e)}")
        frappe.msgprint(
            f"Erpnext Location app installed, but sample data import failed.<br>"
            f"Error: {str(e)}<br>"
            f"You can manually import data later from Settings.",
            title="Installation Warning",
            indicator="orange"
        )
