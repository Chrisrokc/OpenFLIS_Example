import requests
import os
import json

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
    return input("Choose option (1, 2, 3, 4, or 5): ").strip()

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
        else:
            print("Invalid selection. Please choose 1, 2, 3, 4, or 5.")
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