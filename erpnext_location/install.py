# Copyright (c) 2025, Novizna PVT LTD.
# MIT License

import frappe
from erpnext_location.erpnext_location.utils.data_import import refresh_location_data


def after_install():
    """Run after app installation"""
    frappe.logger().info("erpnext_location: Running post-installation setup")

    # Install custom fields using fixtures
    install_custom_fields()

    # Queue location data import as background job
    queue_location_data_import()

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


def queue_location_data_import():
    """Queue location data import as a background job"""
    try:
        frappe.logger().info("Queuing location data import as background job...")

        # Queue the chunked import job to run in background
        frappe.enqueue(
            method="erpnext_location.erpnext_location.utils.data_import.refresh_location_data_chunked",
            queue="long",  # Use long queue for time-consuming tasks
            timeout=3600,  # 1 hour timeout
            force_update=True,
            chunk_size=25,  # Smaller chunks for better progress
            job_name="location_data_import"
        )

        frappe.logger().info("Location data import queued successfully. Check background jobs status.")

        # Create a notification for admin
        frappe.publish_realtime(
            event="location_import_queued",
            message="Location data import has been queued as a background job. This may take several minutes to complete.",
            user=frappe.session.user
        )

    except Exception as e:
        frappe.logger().error(f"Error queuing location data import: {str(e)}")
        frappe.logger().info("You can manually import location data later using: bench execute erpnext_location.erpnext_location.utils.data_import.refresh_location_data")


def manual_location_import():
    """Manual method to import location data - can be called from console"""
    try:
        frappe.logger().info("Starting manual location data import...")
        result = refresh_location_data(force_update=True)
        frappe.logger().info(f"Manual location data import completed: {result}")
        return result
    except Exception as e:
        frappe.logger().error(f"Manual location data import failed: {str(e)}")
        raise


def after_migrate():
    """Execute after migration"""
    frappe.logger().info("Erpnext Location migration completed successfully")

    # Queue location data import as background job instead of running synchronously
    try:
        frappe.logger().info("Queuing location data import after migration...")
        queue_location_data_import()
        frappe.logger().info("Location data import queued successfully")
    except Exception as e:
        frappe.logger().error(f"Error queuing location data import: {str(e)}")
        frappe.logger().info("Location data import can be run manually later using: bench execute erpnext_location.install.manual_location_import")
