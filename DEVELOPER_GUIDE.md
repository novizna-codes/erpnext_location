# ERPNext Location - Developer Quick Reference

## Background Job Implementation

The location data import has been optimized to use Frappe's background job system to prevent installation/migration timeouts.

### Key Changes Made

1. **Background Jobs**: Data import runs in background instead of blocking installation
2. **Chunked Processing**: Large datasets processed in smaller batches
3. **Safe Field Assignment**: Uses `hasattr()` checks to prevent field errors
4. **Progress Monitoring**: Real-time notifications and detailed logging

### Available Methods

#### Installation & Migration Hooks
```python
# In install.py
after_install()          # Runs after app installation
after_migrate()          # Runs after migration
queue_location_data_import()  # Queues background job
manual_location_import()      # Manual import method
```

#### Data Import Methods
```python
# In utils/data_import.py
refresh_location_data(force_update=False)          # Standard import
refresh_location_data_chunked(force_update=False)  # Chunked import with progress
```

#### Scheduled Tasks
```python
# In tasks.py
update_location_data()  # Monthly scheduled update
```

### Safe Field Assignment Helper

The `safe_set_field()` method prevents errors when custom fields don't exist:

```python
def safe_set_field(self, doc, field_name, value, default=""):
    """Safely set a field value on a document if the field exists"""
    if hasattr(doc, field_name):
        setattr(doc, field_name, value if value is not None else default)
        return True
    return False
```

### Usage Examples

#### Queue Background Import
```bash
bench execute erpnext_location.install.queue_location_data_import
```

#### Manual Import with Force Update
```bash
bench execute erpnext_location.install.manual_location_import
```

#### Chunked Import with Custom Parameters
```bash
bench execute erpnext_location.erpnext_location.utils.data_import.refresh_location_data_chunked --kwargs "{'force_update': True, 'chunk_size': 25}"
```

### Monitoring

- **Background Jobs**: Check status in ERPNext Background Jobs
- **Error Logs**: View detailed import logs in Error Log doctype
- **Real-time Notifications**: Receive browser notifications on completion

### Data Sources

All location data imported from: https://github.com/dr5hn/countries-states-cities-database

- Countries: ~250 records
- States: ~4,900 records
- Cities: ~150,000 records
- Regions & Subregions: UN classifications

### Performance Tips

1. Use background jobs for large imports
2. Adjust chunk_size based on server capacity
3. Run during low-traffic periods
4. Monitor database performance during import
5. Use `force_update=False` for incremental updates

### Troubleshooting

1. **Import Fails**: Check Error Log for specific errors
2. **Timeout Issues**: Use smaller chunk_size
3. **Missing Fields**: Ensure fixtures are loaded properly
4. **Network Issues**: Verify GitHub API accessibility
