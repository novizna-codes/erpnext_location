# Copyright (c) 2025, Novizna PVT LTD.
# MIT License

import frappe
from erpnext_location.erpnext_location.utils.data_import import refresh_location_data


def after_install():
    """Run after app installation"""
    frappe.logger().info("erpnext_location: Running post-installation setup")

    # Install custom fields using fixtures
    install_custom_fields()
    refresh_location_data(force_update=True)

    frappe.logger().info("erpnext_location: Post-installation setup completed")


def install_custom_fields():
    """Install custom fields for Country doctype using fixtures"""
    try:
        # Fixtures are automatically loaded during installation
        # Just log that the process is happening - no need to manually reload
        frappe.logger().info("Country custom fields will be loaded from fixtures")

        # Clear any cached doctypes to ensure fresh load
        frappe.clear_cache(doctype="Country")
        frappe.logger().info("Country custom fields loaded from fixtures successfully")
    except Exception as e:
        frappe.logger().error(f"Error with Country custom fields: {str(e)}")
        pass


def after_migrate():
    """Execute after migration"""
    frappe.logger().info("Erpnext Location migration completed successfully")

    # Optional: Refresh location data after migration
    try:
        frappe.logger().info("Starting location data import after migration...")
        refresh_location_data(force_update=True)
        frappe.logger().info("Location data import completed successfully")
    except Exception as e:
        frappe.logger().error(f"Error during location data import: {str(e)}")
        frappe.logger().info("Location data import can be run manually later")
