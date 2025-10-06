import requests
import os
import json

PICA_SERVICE_MAP = {
    "A": "Army",
    "N": "Navy",
    "F": "Air Force",
    "M": "Marine Corps",
    "C": "Coast Guard",
    "D": "Defense Logistics Agency (DLA)",
    "GX": "DLA Land & Maritime",
    "GH": "DLA Aviation",
    "BF": "DLA Troop Support",
    "PA": "DLA Troop Support - Philadelphia",
    "CD": "DLA Aviation (Columbus)",
    "YP": "Foreign Military Sales (FMS) or NATO",
    "ZA": "Commercial Item/NATO",
    "ZH": "GSA",
    "ZW": "Service not otherwise listed",
    "YY": "Special program use",
    "ZB": "GSA",
    "ZN": "NATO (non-US)",
    "ZU": "Obsolete/Discontinued",
    "ZC": "Classified Item",
}

def get_managing_services(moe_records):
    """Extract and deduplicate managing services from MOE_RULE records based on PICA codes"""
    services = []
    seen = set()
    
    for record in moe_records:
        pica = record.get("PICA", "")
        if pica and pica not in seen:
            seen.add(pica)
            service_name = PICA_SERVICE_MAP.get(pica, pica)
            services.append(service_name)
    
    return services

def get_niin_data(niin, table_type):
    """Fetch NIIN data from OpenFLIS API"""
    api_key = os.getenv('OPENFLIS_API_KEY')
    if not api_key:
        print("Error: OPENFLIS_API_KEY environment variable not set")
        return None
    
    # Determine which table to query based on selection
    if table_type == "nsn":
        table = "NSN"
    elif table_type == "history":
        table = "HISTORY_PICK"
    elif table_type == "management_future":
        table = "MANAGEMENT_FUTURE"
    elif table_type == "management":
        table = "MANAGEMENT"
    elif table_type == "army_management":
        table = "MGMT_ARMY"
    elif table_type == "standardization":
        table = "STANDARDIZATION"
    elif table_type == "moe_rule":
        table = "MOE_RULE"
    elif table_type == "management_history":
        table = "MANAGEMENT_HISTORY"
    else:
        print("Invalid table type")
        return None
    
    url = f"https://app.openflis.com/api/v1/query?table={table}&key={niin}&apiKey={api_key}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        
        # Try to parse JSON, fallback to text if not JSON
        try:
            return response.json()
        except json.JSONDecodeError:
            return response.text
            
    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")
        return None

def display_data(data):
    """Display the API response data in a readable format"""
    if data is None:
        print("No data received from API")
        return
    
    print("\n" + "="*60)
    print("NIIN DATA FROM OPENFLIS API")
    print("="*60)
    
    if isinstance(data, dict):
        # If it's a dictionary, display it nicely formatted
        print(json.dumps(data, indent=2))
        
        # If this is MOE_RULE data, show managing services summary
        if data.get("name") == "MOE_RULE" and "records" in data:
            records = data.get("records", [])
            if records:
                services = get_managing_services(records)
                print("\n" + "-"*60)
                print("MANAGING SERVICES SUMMARY:")
                print("Managing Services for this NIIN:", ", ".join(services))
                print("-"*60)
    elif isinstance(data, list):
        # If it's a list, display each item
        for i, item in enumerate(data):
            print(f"Item {i+1}:")
            if isinstance(item, dict):
                print(json.dumps(item, indent=2))
            else:
                print(item)
            print("-" * 40)
    else:
        # If it's plain text or other format
        print(data)
    
    print("="*60)

def show_menu():
    """Display the API endpoint selection menu"""
    print("\nSelect API Endpoint:")
    print("1. FLIS NSN (NSN Table)")
    print("2. History (HISTORY_PICK Table)")
    print("3. Management Future (MANAGEMENT_FUTURE Table)")
    print("4. Management (MANAGEMENT Table)")
    print("5. Army Management (MGMT_ARMY Table)")
    print("6. Standardization (STANDARDIZATION Table)")
    print("7. MOE Rule Coded (MOE_RULE Table)")
    print("8. Management History (MANAGEMENT_HISTORY Table)")
    return input("Choose option (1, 2, 3, 4, 5, 6, 7, or 8): ").strip()

def main():
    """Main application loop"""
    print("OpenFLIS NIIN Data Retrieval Application")
    print("=" * 40)
    
    while True:
        # Show menu and get selection
        selection = show_menu()
        
        if selection == "1":
            table_type = "nsn"
            table_name = "FLIS NSN"
        elif selection == "2":
            table_type = "history"
            table_name = "History"
        elif selection == "3":
            table_type = "management_future"
            table_name = "Management Future"
        elif selection == "4":
            table_type = "management"
            table_name = "Management"
        elif selection == "5":
            table_type = "army_management"
            table_name = "Army Management"
        elif selection == "6":
            table_type = "standardization"
            table_name = "Standardization"
        elif selection == "7":
            table_type = "moe_rule"
            table_name = "MOE Rule Coded"
        elif selection == "8":
            table_type = "management_history"
            table_name = "Management History"
        else:
            print("Invalid selection. Please choose 1, 2, 3, 4, 5, 6, 7, or 8.")
            continue
        
        print(f"\nSelected: {table_name}")
        print("-" * 40)
        
        while True:
            # Prompt for NIIN
            niin = input("\nEnter NIIN (or 'back' to change endpoint, 'quit' to exit): ").strip()
            
            if niin.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                return
            
            if niin.lower() in ['back', 'b']:
                break  # Go back to menu
            
            if not niin:
                print("Please enter a valid NIIN")
                continue
            
            print(f"\nFetching {table_name} data for NIIN: {niin}")
            print("Please wait...")
            
            # Fetch and display data
            data = get_niin_data(niin, table_type)
            display_data(data)

if __name__ == "__main__":
    main()