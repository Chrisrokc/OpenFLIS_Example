# OpenFLIS Data Lookup

A web application for querying military supply chain data from the OpenFLIS (Federal Logistics Information System) API. Search by NSN, NIIN, or Part Number to retrieve comprehensive logistics data.

## Features

- **NSN/NIIN Search** - Enter a full NSN (e.g., 1560-01-162-5517) or just the NIIN (e.g., 011625517)
- **Part Number Search** - Look up items by manufacturer part number
- **Comprehensive Data Display** - View all available data in organized tabs:
  - Item Overview (NSN, NIIN, FSC, Item Name, Managing Service)
  - Management Data (pricing, unit of issue, acquisition codes)
  - MOE Rules (service ownership - PICA, SICA, IMCA)
  - Standardization Status
  - Army-specific Management Data
  - Historical Records
  - Future Management Data
  - Raw API Data

## Requirements

- Python 3.11+
- OpenFLIS API Key (get one at [openflis.com](https://app.openflis.com))

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/openflis-lookup.git
   cd openflis-lookup
   ```

2. Install dependencies:
   ```bash
   pip install streamlit requests pandas
   ```

3. Run the application:
   ```bash
   streamlit run streamlit_app.py --server.port 5000
   ```

4. Open your browser and navigate to `http://localhost:5000`

5. Enter your OpenFLIS API key in the Settings panel

## Usage

1. Enter your API key in the sidebar Settings section
2. Select search type (NSN/NIIN or Part Number)
3. Enter your search query
4. Click Search to retrieve data
5. Browse through the tabs to view different data categories

## Project Structure

```
openflis-lookup/
├── streamlit_app.py      # Main Streamlit web application
├── openflis_client.py    # API client module
├── main.py               # Legacy CLI application
├── README.md             # This file
└── pyproject.toml        # Python project configuration
```

## API Tables Queried

The application queries the following OpenFLIS API tables:

| Table | Description |
|-------|-------------|
| NSN | National Stock Number identification data |
| MANAGEMENT | Current management and pricing data |
| MANAGEMENT_FUTURE | Future management data |
| MANAGEMENT_HISTORY | Historical management records |
| HISTORY_PICK | Historical pick records |
| MGMT_ARMY | Army-specific management data |
| STANDARDIZATION | Item standardization status |
| MOE_RULE | Method of Execution rules (service ownership) |

## Service Code Reference

The application translates service codes to readable names:

| Code | Service |
|------|---------|
| A | Army |
| N | Navy |
| F | Air Force |
| M | Marine Corps |
| C | Coast Guard |
| D | Defense Logistics Agency (DLA) |
| GX | DLA Land & Maritime |
| GH | DLA Aviation |

## License

MIT License

## Acknowledgments

- Data provided by [OpenFLIS](https://app.openflis.com)
- Built with [Streamlit](https://streamlit.io)
