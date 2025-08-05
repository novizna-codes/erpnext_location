# Copyright (c) 2025, Novizna PVT LTD.
# MIT License

import frappe
import requests
import json
import os
from frappe.utils import cint, flt, now


class LocationDataImporter:
    """Import location data from dr5hn/countries-states-cities-database"""

    def __init__(self):
        self.base_url = "https://raw.githubusercontent.com/dr5hn/countries-states-cities-database/master/json"
        self.batch_size = 100

    def safe_set_field(self, doc, field_name, value, default=""):
        """Safely set a field value on a document if the field exists"""
        if hasattr(doc, field_name):
            setattr(doc, field_name, value if value is not None else default)
            return True
        return False

    def import_all_data(self, force_update=False):
        """Import all location data (regions, subregions, countries, states, cities)"""
        frappe.logger().info("Starting location data import from GitHub repository")

        try:
            # Import regions first
            regions_imported = self.import_regions(force_update)
            frappe.logger().info(f"Regions imported: {regions_imported}")

            # Import subregions
            subregions_imported = self.import_subregions(force_update)
            frappe.logger().info(f"Subregions imported: {subregions_imported}")

            # Import countries
            countries_imported = self.import_countries(force_update)
            frappe.logger().info(f"Countries imported: {countries_imported}")

            # Import states
            states_imported = self.import_states(force_update)
            frappe.logger().info(f"States imported: {states_imported}")

            # Import cities
            cities_imported = self.import_cities(force_update)
            frappe.logger().info(f"Cities imported: {cities_imported}")

            # Update import log
            self.log_import_completion(regions_imported, subregions_imported, countries_imported, states_imported, cities_imported)

            return {
                "status": "success",
                "regions": regions_imported,
                "subregions": subregions_imported,
                "countries": countries_imported,
                "states": states_imported,
                "cities": cities_imported
            }

        except Exception as e:
            frappe.logger().error(f"Location data import failed: {str(e)}")
            raise

    def import_regions(self, force_update=False):
        """Import regions data"""
        frappe.logger().info("Importing regions data...")

        regions_data = self.download_data("subregions.json")
        if not regions_data:
            return 0

        imported_count = 0
        for region in regions_data:
            # try:
            # Check if region already exists
            existing_region = frappe.db.exists("Region", {"external_id": str(region["id"])})

            if existing_region and not force_update:
                continue

            if existing_region:
                region_doc = frappe.get_doc("Region", existing_region)
            else:
                region_doc = frappe.new_doc("Region")

            # Map region data
            region_doc.region_name = region["name"]
            self.safe_set_field(region_doc, 'wikidata_id', region.get("wikiDataId", ""))
            self.safe_set_field(region_doc, 'external_id', str(region["id"]))
            self.safe_set_field(region_doc, 'last_updated', now())

            region_doc.save(ignore_permissions=True)
            imported_count += 1

            if imported_count % 10 == 0:
                frappe.db.commit()

            # except Exception as e:
            #     frappe.logger().error(f"Error importing region {region.get('name', 'Unknown')}: {str(e)}")
            #     continue

        frappe.db.commit()
        frappe.logger().info(f"Successfully imported {imported_count} regions")
        return imported_count

    def import_subregions(self, force_update=False):
        """Import subregions data"""
        frappe.logger().info("Importing subregions data...")

        subregions_data = self.download_data("subregions.json")
        if not subregions_data:
            return 0

        imported_count = 0
        for subregion in subregions_data:
            # try:
            # Check if subregion already exists
            existing_subregion = frappe.db.exists("Subregion", {"external_id": str(subregion["id"])})

            if existing_subregion and not force_update:
                continue

            # Find parent region
            region_external_id = str(subregion["region_id"])
            region_name = frappe.db.get_value("Region", {"external_id": region_external_id}, "name")

            if not region_name:
                frappe.logger().warning(f"Region not found for subregion {subregion['name']} (region_id: {region_external_id})")
                continue

            if existing_subregion:
                subregion_doc = frappe.get_doc("Subregion", existing_subregion)
            else:
                subregion_doc = frappe.new_doc("Subregion")

            # Map subregion data
            subregion_doc.subregion_name = subregion["name"]
            subregion_doc.region = region_name
            self.safe_set_field(subregion_doc, 'wikidata_id', subregion.get("wikiDataId", ""))
            self.safe_set_field(subregion_doc, 'external_id', str(subregion["id"]))
            self.safe_set_field(subregion_doc, 'last_updated', now())

            subregion_doc.save(ignore_permissions=True)
            imported_count += 1

            if imported_count % 10 == 0:
                frappe.db.commit()

            # except Exception as e:
            #     frappe.logger().error(f"Error importing subregion {subregion.get('name', 'Unknown')}: {str(e)}")
            #     continue

        frappe.db.commit()
        frappe.logger().info(f"Successfully imported {imported_count} subregions")
        return imported_count

    def import_countries(self, force_update=False):
        """Import countries data"""
        frappe.logger().info("Importing countries data...")

        # Download countries data
        countries_data = self.download_data("countries.json")
        if not countries_data:
            return 0

        imported_count = 0

        for country in countries_data:
            try:
                country_name = country.get("name", "").strip()
                iso2_code = country.get("iso2", "").strip().lower()
                if not country_name:
                    continue

                # Check if country exists
                # Prefer iso2 (code), then iso3, then name for lookup
                existing_country = None
                existing_country_name = None

                if country.get("iso2"):
                    existing_country_name = frappe.db.get_value("Country", {"code": country.get("iso2", "").strip().lower()}, "country_name")
                    if existing_country_name:
                        existing_country = existing_country_name

                if not existing_country and country.get("iso3"):
                    existing_country_name = frappe.db.get_value("Country", {"iso3": country.get("iso3", "").strip().lower()}, "country_name")
                    if existing_country_name:
                        existing_country = existing_country_name

                if not existing_country:
                    existing_country_name = frappe.db.get_value("Country", {"name": country_name}, "country_name")
                    if existing_country_name:
                        existing_country = existing_country_name

                if existing_country and not force_update:
                    continue

                # Create or update country
                if existing_country:
                    country_doc = frappe.get_doc("Country", existing_country)
                else:
                    country_doc = frappe.new_doc("Country")
                    country_doc.country_name = country_name

                # Update country fields
                if country.get("iso2"):
                    country_doc.code = iso2_code
                    self.safe_set_field(country_doc, 'iso2', iso2_code)

                country_doc.flags.ignore_mandatory = True

                # Set geographic and basic fields
                self.safe_set_field(country_doc, 'latitude', country.get("latitude", ""))
                self.safe_set_field(country_doc, 'longitude', country.get("longitude", ""))
                self.safe_set_field(country_doc, 'emoji', country.get("emoji", ""))
                self.safe_set_field(country_doc, 'emojiU', country.get("emojiU", ""))

                # Add custom fields data
                self.safe_set_field(country_doc, 'iso3', country.get("iso3", "").strip().lower())
                self.safe_set_field(country_doc, 'numeric_code', country.get("numeric_code", ""))
                self.safe_set_field(country_doc, 'phonecode', country.get("phonecode", ""))
                self.safe_set_field(country_doc, 'capital', country.get("capital", ""))
                self.safe_set_field(country_doc, 'currency_name', country.get("currency_name", ""))
                self.safe_set_field(country_doc, 'currency_symbol', country.get("currency_symbol", ""))
                self.safe_set_field(country_doc, 'tld', country.get("tld", ""))
                self.safe_set_field(country_doc, 'native', country.get("native", ""))

                # Link to Region and Subregion DocTypes
                if country.get("region"):
                    region_name = frappe.db.get_value("Region", {"region_name": country["region"]}, "name")
                    if region_name:
                        self.safe_set_field(country_doc, 'region', region_name)

                if country.get("subregion"):
                    subregion_name = frappe.db.get_value("Subregion", {"subregion_name": country["subregion"]}, "name")
                    if subregion_name:
                        self.safe_set_field(country_doc, 'subregion', subregion_name)

                self.safe_set_field(country_doc, 'nationality', country.get("nationality", ""))
                self.safe_set_field(country_doc, 'external_id', str(country.get("id", "")))
                self.safe_set_field(country_doc, 'last_updated', now())

                country_doc.save(ignore_permissions=True)
                imported_count += 1

                if imported_count % 50 == 0:
                    frappe.db.commit()
                    frappe.logger().info(f"Imported {imported_count} countries...")

            except Exception as e:
                frappe.logger().error(f"Error importing country {country.get('name', 'Unknown')}: {str(e)}")
                print(f"Error importing {country_name}: {str(e)}")
                continue

        frappe.db.commit()
        frappe.logger().info(f"Successfully imported {imported_count} countries")
        return imported_count

    def import_states(self, force_update=False):
        """Import states data"""
        frappe.logger().info("Importing states data...")

        # Download states data
        states_data = self.download_data("states.json")
        if not states_data:
            return 0

        imported_count = 0

        for state in states_data:
            # try:
            state_name = state.get("name", "").strip()
            country_code = state.get("country_code", "").strip().lower()

            if not state_name or not country_code:
                continue

            # Find country by code
            country_name = frappe.db.get_value("Country", {"code": country_code}, "name")
            if not country_name:
                continue

            # Check if state exists
            existing_state = frappe.db.exists("State", state_name)

            if existing_state and not force_update:
                continue

            # Create or update state
            if existing_state:
                state_doc = frappe.get_doc("State", existing_state)
            else:
                state_doc = frappe.new_doc("State")
                state_doc.state_name = state_name

            # Update state fields
            self.safe_set_field(state_doc, 'state_code', state.get("iso2", ""))
            state_doc.country = country_name
            self.safe_set_field(state_doc, 'country_code', country_code)
            self.safe_set_field(state_doc, 'state_type', state.get("type", ""))
            self.safe_set_field(state_doc, 'fips_code', state.get("fips_code", ""))

            # Geographic data
            if state.get("latitude"):
                self.safe_set_field(state_doc, 'latitude', flt(state.get("latitude")))
            if state.get("longitude"):
                self.safe_set_field(state_doc, 'longitude', flt(state.get("longitude")))

            # System fields
            self.safe_set_field(state_doc, 'external_id', str(state.get("id", "")))
            self.safe_set_field(state_doc, 'last_updated', now())
            self.safe_set_field(state_doc, 'is_active', 1)

            state_doc.save(ignore_permissions=True)
            imported_count += 1

            if imported_count % 100 == 0:
                frappe.db.commit()
                frappe.logger().info(f"Imported {imported_count} states...")

            # except Exception as e:
            #     frappe.logger().error(f"Error importing state {state.get('name', 'Unknown')}: {str(e)}")
            #     continue

        frappe.db.commit()
        frappe.logger().info(f"Successfully imported {imported_count} states")
        return imported_count

    def import_cities(self, force_update=False):
        """Import cities data (with batching due to large dataset)"""
        frappe.logger().info("Importing cities data...")

        # Download cities data
        cities_data = self.download_data("cities.json")
        if not cities_data:
            return 0

        imported_count = 0
        batch_count = 0

        # Process in batches
        for i in range(0, len(cities_data), self.batch_size):
            batch = cities_data[i:i + self.batch_size]
            batch_count += 1

            for city in batch:
                # try:
                city_name = city.get("name", "").strip()
                state_name = city.get("state_name", "").strip()
                country_code = city.get("country_code", "").strip().lower()

                if not city_name or not state_name or not country_code:
                    continue

                # Find state
                existing_state = frappe.db.exists("State", state_name)
                if not existing_state:
                    continue

                # Create unique city identifier
                city_identifier = f"{city_name}-{state_name}"

                # Check if city exists
                existing_city = frappe.db.exists("City", {"name": city_identifier})

                if existing_city and not force_update:
                    continue

                # Create or update city
                if existing_city:
                    city_doc = frappe.get_doc("City", existing_city)
                else:
                    city_doc = frappe.new_doc("City")
                    city_doc.city_name = city_name
                    city_doc.state = state_name

                # Get country from state
                state_doc = frappe.get_doc("State", state_name)
                city_doc.country = state_doc.country
                self.safe_set_field(city_doc, 'country_code', state_doc.country_code)
                self.safe_set_field(city_doc, 'state_code', state_doc.state_code)

                # Geographic data
                if city.get("latitude"):
                    self.safe_set_field(city_doc, 'latitude', flt(city.get("latitude")))
                if city.get("longitude"):
                    self.safe_set_field(city_doc, 'longitude', flt(city.get("longitude")))

                # Reference data
                self.safe_set_field(city_doc, 'wikidata_id', city.get("wikiDataId", ""))
                self.safe_set_field(city_doc, 'external_id', str(city.get("id", "")))
                self.safe_set_field(city_doc, 'last_updated', now())
                self.safe_set_field(city_doc, 'is_active', 1)

                city_doc.save(ignore_permissions=True)
                imported_count += 1

                # except Exception as e:
                #     frappe.logger().error(f"Error importing city {city.get('name', 'Unknown')}: {str(e)}")
                #     continue

            # Commit after each batch
            frappe.db.commit()
            frappe.logger().info(f"Processed batch {batch_count}, imported {imported_count} cities so far...")

        frappe.logger().info(f"Successfully imported {imported_count} cities")
        return imported_count

    def download_data(self, filename):
        """Download data from GitHub repository"""
        url = f"{self.base_url}/{filename}"

        try:
            frappe.logger().info(f"Downloading {filename} from GitHub...")
            response = requests.get(url, timeout=300)
            response.raise_for_status()

            data = response.json()
            frappe.logger().info(f"Downloaded {len(data)} records from {filename}")
            return data

        except Exception as e:
            frappe.logger().error(f"Failed to download {filename}: {str(e)}")
            return None

    def log_import_completion(self, regions, subregions, countries, states, cities):
        """Log import completion in system"""
        frappe.logger().info(f"Location data import completed - Regions: {regions}, Subregions: {subregions}, Countries: {countries}, States: {states}, Cities: {cities}")


def refresh_location_data(force_update=False):
    """Refresh all location data - called by scheduled job"""
    importer = LocationDataImporter()
    return importer.import_all_data(force_update)


def refresh_location_data_chunked(force_update=False, chunk_size=50):
    """Refresh location data in smaller chunks with progress updates"""
    frappe.logger().info("Starting chunked location data import...")

    try:
        importer = LocationDataImporter()

        # Set smaller batch size for better progress tracking
        original_batch_size = importer.batch_size
        importer.batch_size = chunk_size

        # Import with progress updates
        result = importer.import_all_data(force_update)

        # Restore original batch size
        importer.batch_size = original_batch_size

        # Publish completion notification
        frappe.publish_realtime(
            event="location_import_completed",
            message=f"Location data import completed successfully. {result}",
            user="Administrator"
        )

        return result

    except Exception as e:
        frappe.logger().error(f"Chunked location data import failed: {str(e)}")

        # Publish error notification
        frappe.publish_realtime(
            event="location_import_failed",
            message=f"Location data import failed: {str(e)}",
            user="Administrator"
        )

        raise
