# Copyright (c) 2025, Novizna PVT LTD.
# MIT License

import frappe
from erpnext_location.erpnext_location.utils.data_import import refresh_location_data


def update_location_data():
    """Scheduled task to update location data monthly"""
    try:
        frappe.logger().info("Starting scheduled location data update")

        # Check if auto-update is enabled (you can add a settings doctype for this)
        # For now, we'll run the update as a background job to avoid blocking

        # Queue the update as background job
        frappe.enqueue(
            method="erpnext_location.erpnext_location.utils.data_import.refresh_location_data_chunked",
            queue="long",
            timeout=3600,
            force_update=False,  # Don't force update existing records for scheduled runs
            chunk_size=50,
            job_name="scheduled_location_data_update"
        )

        frappe.logger().info("Scheduled location data update queued successfully")

        return {"status": "queued", "message": "Location data update queued as background job"}

    except Exception as e:
        frappe.logger().error(f"Scheduled location data update failed: {str(e)}")
        raise
