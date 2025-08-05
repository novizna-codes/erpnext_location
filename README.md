### Erpnext Location

Erpnext app that adds comprehensive location functionality including countries, regions, subregions, states, and cities with geographic data.

## Features

- **Enhanced Country DocType**: Adds custom fields for ISO codes, geographic coordinates, currency information, and timezone data
- **Location Hierarchy**: Regions → Subregions → Countries → States → Cities
- **Automatic Data Import**: Imports location data from [dr5hn/countries-states-cities-database](https://github.com/dr5hn/countries-states-cities-database)
- **Background Processing**: Uses Frappe's job queue for efficient data import
- **Fixtures Support**: Uses fixtures for reliable custom field management

## Installation

You can install this app using the [bench](https://github.com/novizna-codes/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch develop
bench install-app erpnext_location
```

## Location Data Import

### Automatic Import

The app automatically queues location data import as a background job during installation and migration:

- **Installation**: After app installation, location data import is queued automatically
- **Migration**: After app migration, location data import is queued automatically
- **Scheduled**: Monthly automatic updates (can be configured in hooks.py)

### Manual Import Options

If you need to manually import or refresh location data, you have several options:

#### 1. Background Job (Recommended)
```bash
# Queue import as background job
bench execute erpnext_location.install.queue_location_data_import
```

#### 2. Manual Console Import
```bash
# Run import directly (blocking)
bench execute erpnext_location.install.manual_location_import
```

#### 3. Chunked Import (For Large Datasets)
```bash
# Run chunked import with progress updates
bench execute erpnext_location.erpnext_location.utils.data_import.refresh_location_data_chunked --kwargs "{'force_update': True, 'chunk_size': 25}"
```

#### 4. Standard Import
```bash
# Run standard import
bench execute erpnext_location.erpnext_location.utils.data_import.refresh_location_data --kwargs "{'force_update': True}"
```

### Import Parameters

- `force_update=True`: Updates existing records with new data
- `force_update=False`: Only imports new records (default for scheduled runs)
- `chunk_size`: Number of records processed in each batch (default: 100)

### Monitoring Import Progress

- Check **Background Jobs** in ERPNext to monitor import progress
- View logs in **Error Log** for detailed import information
- Real-time notifications are sent when import completes or fails

## Data Sources

The app imports location data from the comprehensive [countries-states-cities-database](https://github.com/dr5hn/countries-states-cities-database) repository by **[@dr5hn](https://github.com/dr5hn)** (Darshan Gada), which includes:

- **250+ Countries** with ISO codes, geographic data, currency info
- **4,900+ States/Provinces** with geographic coordinates
- **150,000+ Cities** with latitude/longitude data
- **Regions and Subregions** following UN classifications

This high-quality, regularly updated dataset is provided under MIT license and has become a standard resource for location data in many applications worldwide.

## Custom Fields Added to Country DocType

- `iso2`: ISO 3166-1 alpha-2 code
- `iso3`: ISO 3166-1 alpha-3 code
- `numeric_code`: ISO 3166-1 numeric code
- `phonecode`: International dialing code
- `capital`: Capital city
- `currency_name`: Currency name
- `currency_symbol`: Currency symbol
- `tld`: Top-level domain
- `native`: Native name
- `latitude`: Geographic latitude
- `longitude`: Geographic longitude
- `emoji`: Flag emoji
- `emojiU`: Unicode flag representation
- `nationality`: Nationality/demonym
- `region`: UN region classification
- `subregion`: UN subregion classification

## Troubleshooting

### Import Issues

If location data import fails:

1. Check **Error Log** for specific error messages
2. Verify internet connectivity for GitHub API access
3. Check available disk space for large datasets
4. Try chunked import for better error isolation:
   ```bash
   bench execute erpnext_location.erpnext_location.utils.data_import.refresh_location_data_chunked --kwargs "{'chunk_size': 10}"
   ```

### Performance Optimization

- Use background jobs for large imports to avoid timeouts
- Adjust `chunk_size` based on server performance
- Schedule imports during low-traffic periods
- Monitor database performance during large imports

## Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/erpnext_location
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade

## CI

This app can use GitHub Actions for CI. The following workflows are configured:

- CI: Installs this app and runs unit tests on every push to `develop` branch.
- Linters: Runs [Frappe Semgrep Rules](https://github.com/frappe/semgrep-rules) and [pip-audit](https://pypi.org/project/pip-audit/) on every pull request.

## License

MIT

## Credits

This app uses location data from the excellent [countries-states-cities-database](https://github.com/dr5hn/countries-states-cities-database) repository created and maintained by **[@dr5hn](https://github.com/dr5hn)** (Darshan Gada).

The database provides comprehensive, up-to-date location data including:
- 250+ Countries with ISO codes, geographic coordinates, and metadata
- 4,900+ States/Provinces with detailed geographic information
- 150,000+ Cities with latitude/longitude coordinates
- UN Region and Subregion classifications
- Currency and timezone information

We are grateful for this well-maintained, open-source resource that makes global location data easily accessible to developers worldwide.

**Repository**: https://github.com/dr5hn/countries-states-cities-database
**Author**: Darshan Gada ([@dr5hn](https://github.com/dr5hn))
**License**: MIT
