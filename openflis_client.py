import requests
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

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

SERVICE_CODE_MAP = {
    "A": "Army",
    "F": "Air Force",
    "N": "Navy",
    "M": "Marine Corps",
    "C": "Coast Guard",
    "D": "DLA",
    "GX": "DLA Land & Maritime",
    "GH": "DLA Aviation",
    "BF": "DLA Troop Support",
    "PA": "DLA Troop Support - Philadelphia",
    "CD": "DLA Aviation (Columbus)",
    "SX": "Air Force",
    "YP": "Foreign Military Sales (FMS)",
    "ZA": "NATO/Commercial",
    "ZH": "GSA",
    "ZW": "Service not otherwise listed",
    "YY": "Special Program Use",
    "ZB": "GSA",
    "ZN": "NATO (non-US)",
    "ZU": "Obsolete/Discontinued",
    "ZC": "Classified Item"
}

API_BASE_URL = "https://app.openflis.com/api/v1/query"

_custom_api_key = None

def get_api_key():
    if _custom_api_key:
        return _custom_api_key
    return os.getenv('OPENFLIS_API_KEY')

def set_api_key(key):
    global _custom_api_key
    _custom_api_key = key

def query_table(table_name, key, api_key=None):
    effective_api_key = api_key or get_api_key()
    if not effective_api_key:
        return {"error": "API key not configured", "records": []}
    
    url = f"{API_BASE_URL}?table={table_name}&key={key}&apiKey={effective_api_key}"
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e), "records": []}

def get_nsn_data(niin):
    return query_table("NSN", niin)

def get_management_data(niin):
    return query_table("MANAGEMENT", niin)

def get_management_future_data(niin):
    return query_table("MANAGEMENT_FUTURE", niin)

def get_management_history_data(niin):
    return query_table("MANAGEMENT_HISTORY", niin)

def get_history_data(niin):
    return query_table("HISTORY_PICK", niin)

def get_army_management_data(niin):
    return query_table("MGMT_ARMY", niin)

def get_standardization_data(niin):
    return query_table("STANDARDIZATION", niin)

def get_moe_rule_data(niin):
    return query_table("MOE_RULE", niin)

def translate_service_code(code):
    return SERVICE_CODE_MAP.get(code, code) if code else ""

def translate_pica_code(code):
    return PICA_SERVICE_MAP.get(code, code) if code else ""

def analyze_service_ownership(moe_records):
    managing_service = None
    user_codes = set()
    
    for record in moe_records:
        sica = record.get("SICA", "").strip()
        if sica and not managing_service:
            managing_service = translate_service_code(sica)
        
        for field in ["SICA", "IMCA"]:
            code = record.get(field, "").strip()
            if code:
                user_codes.add(code)
        
        for field in ["AUTH_RCVR", "AUTH_COLLAB"]:
            codes = record.get(field, "").strip()
            if codes:
                for code in codes.split():
                    if code:
                        user_codes.add(code)
    
    user_services = []
    for code in sorted(user_codes):
        service_name = translate_service_code(code)
        if service_name not in user_services:
            user_services.append(service_name)
    
    return {
        "managing_service": managing_service if managing_service else "Unknown",
        "user_services": user_services
    }

def parse_nsn_input(user_input):
    cleaned = user_input.strip().upper()
    
    if '-' in cleaned:
        parts = cleaned.split('-')
        if len(parts) == 2 and len(parts[0]) == 4:
            return parts[1], parts[0]
        elif len(parts) == 4:
            fsc = parts[0]
            niin = ''.join(parts[1:])
            return niin, fsc
    
    digits_only = ''.join(c for c in cleaned if c.isdigit())
    
    if len(digits_only) == 13:
        return digits_only[4:], digits_only[:4]
    elif len(digits_only) >= 7 and len(digits_only) <= 9:
        return digits_only.zfill(9), None
    
    return cleaned, None

def get_comprehensive_data(niin):
    results = {}
    
    tables = {
        'nsn': get_nsn_data,
        'management': get_management_data,
        'management_future': get_management_future_data,
        'management_history': get_management_history_data,
        'history': get_history_data,
        'army_management': get_army_management_data,
        'standardization': get_standardization_data,
        'moe_rule': get_moe_rule_data
    }
    
    with ThreadPoolExecutor(max_workers=8) as executor:
        future_to_table = {executor.submit(func, niin): name for name, func in tables.items()}
        
        for future in as_completed(future_to_table):
            table_name = future_to_table[future]
            try:
                results[table_name] = future.result()
            except Exception as e:
                results[table_name] = {"error": str(e), "records": []}
    
    return results

def build_item_overview(niin, comprehensive_data):
    overview = {
        "niin": niin,
        "nsn": "",
        "fsc": "",
        "item_name": "",
        "managing_service": "",
        "user_services": [],
        "sos": "",
        "cancelled_niin": "",
        "end_item": ""
    }
    
    nsn_data = comprehensive_data.get('nsn', {})
    if nsn_data.get('records'):
        record = nsn_data['records'][0]
        overview['fsc'] = record.get('FSC', '')
        overview['item_name'] = record.get('ITEM_NAME', '')
        overview['sos'] = record.get('SOS', '')
        overview['cancelled_niin'] = record.get('CANCELLED_NIIN', '')
        overview['end_item'] = record.get('END_ITEM_NAME', '')
        
        if overview['fsc']:
            overview['nsn'] = f"{overview['fsc']}-{niin}"
    
    moe_data = comprehensive_data.get('moe_rule', {})
    if moe_data.get('records'):
        ownership = analyze_service_ownership(moe_data['records'])
        overview['managing_service'] = ownership['managing_service']
        overview['user_services'] = ownership['user_services']
    
    return overview

def format_currency(value):
    try:
        if isinstance(value, str):
            value = float(value)
        return f"${value:,.2f}"
    except (ValueError, TypeError):
        return value if value else "N/A"

def format_management_record(record):
    return {
        "Effective Date": record.get("EFFECTIVE_DATE", ""),
        "MOE": record.get("MOE", ""),
        "AAC": record.get("AAC", ""),
        "SOS": record.get("SOS", ""),
        "Unit of Issue": record.get("UI", ""),
        "Unit Price": format_currency(record.get("UNIT_PRICE", "")),
        "QUP": record.get("QUP", ""),
        "CIIC": record.get("CIIC", ""),
        "SLC": record.get("SLC", ""),
        "USC": record.get("USC", ""),
        "Management Control": record.get("MGMT_CTL", "")
    }

def format_moe_record(record):
    return {
        "MOE Rule": record.get("MOE_RULE", ""),
        "PICA": translate_pica_code(record.get("PICA", "")),
        "SICA": translate_service_code(record.get("SICA", "")),
        "IMCA": translate_service_code(record.get("IMCA", "")),
        "Auth Receiver": record.get("AUTH_RCVR", ""),
        "Auth Collab": record.get("AUTH_COLLAB", ""),
        "Effective Date": record.get("EFFECTIVE_DATE", "")
    }

def format_standardization_record(record):
    isc_meanings = {
        "0": "Standard",
        "1": "Provisionally Standard",
        "2": "Conditionally Standard",
        "3": "Substitute",
        "4": "Limited Standard",
        "5": "Declining Stock",
        "6": "Non-Standard",
        "7": "Phased Out",
        "8": "Reserved",
        "9": "Cancelled"
    }
    
    return {
        "ISC": record.get("ISC", "") + f" ({isc_meanings.get(record.get('ISC', ''), 'Unknown')})",
        "Original Standardization Decision": record.get("ORIG_STDZN_DEC", ""),
        "Decision Date": record.get("DT_STDZN_DEC", ""),
        "NIIN Status Code": record.get("NIIN_STAT_CD", ""),
        "Related NSN": record.get("RELATED_NSN", "")
    }

def format_army_management_record(record):
    return {
        "AAC": record.get("AAC", ""),
        "ARC": record.get("ARC", ""),
        "CIIC": record.get("CIIC", ""),
        "Controlled Inv Item Code": record.get("CIIC", ""),
        "Demil Code": record.get("DEMIL_CD", ""),
        "Effective Date": record.get("EFFECTIVE_DATE", ""),
        "ECC": record.get("ECC", ""),
        "HAZMAT": record.get("HAZMAT", ""),
        "SLC": record.get("SLC", ""),
        "UI": record.get("UI", ""),
        "Unit Price": format_currency(record.get("UNIT_PRICE", ""))
    }

def lookup_by_part_number(part_number):
    api_key = get_api_key()
    if not api_key:
        return {
            "Part Number": part_number,
            "NIIN": "",
            "NSN": "",
            "FSC": "",
            "Item Name": "",
            "Matched": False,
            "error": "API key not configured"
        }
    
    data = query_table("NSN", part_number)
    
    if data.get("error"):
        return {
            "Part Number": part_number,
            "NIIN": "",
            "NSN": "",
            "FSC": "",
            "Item Name": "",
            "Matched": False,
            "error": data.get("error")
        }
    
    records = data.get("records", [])
    
    if not records:
        return {
            "Part Number": part_number,
            "NIIN": "",
            "NSN": "",
            "FSC": "",
            "Item Name": "",
            "Matched": False
        }
    
    record = records[0]
    fsc = record.get("FSC", "")
    inc = record.get("INC", "")
    item_name = record.get("ITEM_NAME", "")
    
    niin = inc.zfill(9) if inc else ""
    nsn = f"{fsc}-{niin}" if fsc and niin else ""
    
    return {
        "Part Number": part_number,
        "NIIN": niin,
        "NSN": nsn,
        "FSC": fsc,
        "Item Name": item_name,
        "Matched": True
    }
