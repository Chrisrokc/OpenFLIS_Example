# OpenFLIS Data Lookup Application

## Overview
A web application for querying military supply chain data from the OpenFLIS (Federal Logistics Information System) API. Users can search by NSN (National Stock Number), NIIN (National Item Identification Number), or Part Number to retrieve comprehensive logistics data.

## Project Architecture

### Files
- `streamlit_app.py` - Main Streamlit web application with UI components
- `openflis_client.py` - API client module with all OpenFLIS API functions
- `main.py` - Legacy CLI application (kept for reference)

### Key Features
- NSN/NIIN search as primary action
- Part Number lookup with automatic NIIN resolution
- Parallel API queries for performance
- Cached results (5-minute TTL)
- Tabbed interface for different data categories

### Data Categories
1. **Item Overview** - NSN, NIIN, FSC, Item Name, Managing Service
2. **Management** - Pricing, Unit of Issue, Management codes
3. **MOE Rules** - Service ownership (PICA, SICA, IMCA codes)
4. **Standardization** - ISC codes and status
5. **Army Management** - Army-specific data
6. **History** - Historical records
7. **Management Future** - Future management data

## API Integration
- Base URL: `https://app.openflis.com/api/v1/query`
- Authentication: API key via `OPENFLIS_API_KEY` environment variable
- Tables: NSN, MANAGEMENT, MANAGEMENT_FUTURE, MANAGEMENT_HISTORY, HISTORY_PICK, MGMT_ARMY, STANDARDIZATION, MOE_RULE

## Running the Application
The Streamlit app runs on port 5000:
```
streamlit run streamlit_app.py --server.port 5000 --server.address 0.0.0.0 --server.headless true
```

## Recent Changes
- Migrated from CLI to Streamlit web interface
- Added parallel API queries with ThreadPoolExecutor
- Implemented 5-minute result caching
- Added comprehensive data display with tabs
- Service code translation (PICA, SICA to readable names)
