import requests
import os
import json

def get_niin_data(niin):
    """Fetch NIIN data from OpenFLIS API"""
    api_key = os.getenv('OPENFLIS_API_KEY')
    if not api_key:
        print("Error: OPENFLIS_API_KEY environment variable not set")
        return None
    
    url = f"https://app.openflis.com/api/v1/query?table=NSN&key={niin}&apiKey={api_key}"
    
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

def main():
    """Main application loop"""
    print("OpenFLIS NIIN Data Retrieval Application")
    print("-" * 40)
    
    while True:
        # Prompt for NIIN
        niin = input("\nEnter NIIN (or 'quit' to exit): ").strip()
        
        if niin.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        if not niin:
            print("Please enter a valid NIIN")
            continue
        
        print(f"\nFetching data for NIIN: {niin}")
        print("Please wait...")
        
        # Fetch and display data
        data = get_niin_data(niin)
        display_data(data)

if __name__ == "__main__":
    main()