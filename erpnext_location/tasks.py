# Copyright (c) 2025, Novizna PVT LTD.
# MIT License

import frappe
from erpnext_location.erpnext_location.utils.data_import import refresh_location_data


def update_location_data():
    """Scheduled task to update location data weekly"""
    try:
        frappe.logger().info("Starting scheduled location data update")

        # Check if auto-update is enabled (you can add a settings doctype for this)
        # For now, we'll run the update

        result = refresh_location_data(force_update=False)

        frappe.logger().info(f"Scheduled location data update completed: {result}")

        return result

    except Exception as e:
        frappe.logger().error(f"Scheduled location data update failed: {str(e)}")
        raise
