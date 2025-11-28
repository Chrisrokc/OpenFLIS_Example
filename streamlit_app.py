import streamlit as st
import pandas as pd
from openflis_client import (
    get_comprehensive_data,
    build_item_overview,
    parse_nsn_input,
    lookup_by_part_number,
    format_management_record,
    format_moe_record,
    format_standardization_record,
    format_army_management_record,
    get_api_key,
    set_api_key
)

@st.cache_data(ttl=300, show_spinner=False)
def cached_get_comprehensive_data(niin):
    return get_comprehensive_data(niin)

@st.cache_data(ttl=300, show_spinner=False)
def cached_lookup_by_part_number(part_number):
    return lookup_by_part_number(part_number)

st.set_page_config(
    page_title="OpenFLIS Data Lookup",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E3A5F;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1E3A5F;
    }
    .section-header {
        font-size: 1.3rem;
        font-weight: bold;
        color: #1E3A5F;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #e0e0e0;
    }
    .info-label {
        font-weight: bold;
        color: #444;
    }
    .info-value {
        color: #1E3A5F;
    }
    .stDataFrame {
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

def init_session_state():
    if 'search_results' not in st.session_state:
        st.session_state.search_results = None
    if 'last_search' not in st.session_state:
        st.session_state.last_search = ""
    if 'search_type' not in st.session_state:
        st.session_state.search_type = "NSN/NIIN"
    if 'user_api_key' not in st.session_state:
        st.session_state.user_api_key = ""

def display_item_overview(overview):
    st.markdown('<p class="section-header">📋 Item Overview</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("NSN", overview.get('nsn', 'N/A') or 'N/A')
        st.metric("FSC", overview.get('fsc', 'N/A') or 'N/A')
    
    with col2:
        st.metric("NIIN", overview.get('niin', 'N/A') or 'N/A')
        st.metric("SOS", overview.get('sos', 'N/A') or 'N/A')
    
    with col3:
        st.metric("Managing Service", overview.get('managing_service', 'N/A') or 'N/A')
        if overview.get('cancelled_niin'):
            st.warning(f"⚠️ Cancelled NIIN: {overview['cancelled_niin']}")
    
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"**Item Name:** {overview.get('item_name', 'N/A') or 'N/A'}")
        if overview.get('end_item'):
            st.markdown(f"**End Item Application:** {overview.get('end_item')}")
    
    with col2:
        if overview.get('user_services'):
            st.markdown("**User Services:**")
            for service in overview['user_services']:
                st.markdown(f"• {service}")

def display_management_data(management_data):
    st.markdown('<p class="section-header">💰 Management Data</p>', unsafe_allow_html=True)
    
    records = management_data.get('records', [])
    
    if not records:
        st.info("No management data available for this item.")
        return
    
    formatted_records = [format_management_record(r) for r in records]
    df = pd.DataFrame(formatted_records)
    
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    if records:
        first_record = records[0]
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Unit of Issue", first_record.get("UI", "N/A"))
        with col2:
            price = first_record.get("UNIT_PRICE", "")
            try:
                price_val = float(price) if price else 0
                st.metric("Unit Price", f"${price_val:,.2f}")
            except:
                st.metric("Unit Price", "N/A")
        with col3:
            st.metric("AAC", first_record.get("AAC", "N/A"))
        with col4:
            st.metric("CIIC", first_record.get("CIIC", "N/A"))

def display_moe_rules(moe_data):
    st.markdown('<p class="section-header">📜 MOE Rules (Service Ownership)</p>', unsafe_allow_html=True)
    
    records = moe_data.get('records', [])
    
    if not records:
        st.info("No MOE rule data available for this item.")
        return
    
    formatted_records = [format_moe_record(r) for r in records]
    df = pd.DataFrame(formatted_records)
    
    st.dataframe(df, use_container_width=True, hide_index=True)

def display_standardization(std_data):
    st.markdown('<p class="section-header">📊 Standardization Status</p>', unsafe_allow_html=True)
    
    records = std_data.get('records', [])
    
    if not records:
        st.info("No standardization data available for this item.")
        return
    
    formatted_records = [format_standardization_record(r) for r in records]
    df = pd.DataFrame(formatted_records)
    
    st.dataframe(df, use_container_width=True, hide_index=True)

def display_army_management(army_data):
    st.markdown('<p class="section-header">🎖️ Army Management Data</p>', unsafe_allow_html=True)
    
    records = army_data.get('records', [])
    
    if not records:
        st.info("No Army-specific management data available for this item.")
        return
    
    formatted_records = [format_army_management_record(r) for r in records]
    df = pd.DataFrame(formatted_records)
    
    st.dataframe(df, use_container_width=True, hide_index=True)

def display_history(history_data):
    st.markdown('<p class="section-header">📚 History</p>', unsafe_allow_html=True)
    
    records = history_data.get('records', [])
    
    if not records:
        st.info("No history data available for this item.")
        return
    
    df = pd.DataFrame(records)
    st.dataframe(df, use_container_width=True, hide_index=True)

def display_management_future(future_data):
    st.markdown('<p class="section-header">🔮 Management Future</p>', unsafe_allow_html=True)
    
    records = future_data.get('records', [])
    
    if not records:
        st.info("No future management data available for this item.")
        return
    
    df = pd.DataFrame(records)
    st.dataframe(df, use_container_width=True, hide_index=True)

def display_management_history(mgmt_history_data):
    st.markdown('<p class="section-header">📖 Management History</p>', unsafe_allow_html=True)
    
    records = mgmt_history_data.get('records', [])
    
    if not records:
        st.info("No management history data available for this item.")
        return
    
    df = pd.DataFrame(records)
    st.dataframe(df, use_container_width=True, hide_index=True)

def display_raw_data(comprehensive_data):
    st.markdown('<p class="section-header">🔧 Raw API Data</p>', unsafe_allow_html=True)
    
    for table_name, data in comprehensive_data.items():
        with st.expander(f"{table_name.upper().replace('_', ' ')} ({len(data.get('records', []))} records)"):
            if data.get('error'):
                st.error(f"Error: {data['error']}")
            elif data.get('records'):
                df = pd.DataFrame(data['records'])
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("No records found.")

def main():
    init_session_state()
    
    if st.session_state.user_api_key:
        set_api_key(st.session_state.user_api_key)
    
    st.markdown('<p class="main-header">🔍 OpenFLIS Data Lookup</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Federal Logistics Information System - NSN & NIIN Data Retrieval</p>', unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("### Settings")
        
        env_key = get_api_key()
        has_env_key = bool(env_key) and not st.session_state.user_api_key
        
        if has_env_key:
            st.success("API Key configured via environment")
        
        with st.expander("API Key Configuration", expanded=not env_key):
            st.markdown("Enter your OpenFLIS API key below. You can get one from [openflis.com](https://app.openflis.com).")
            
            api_key_input = st.text_input(
                "API Key:",
                value=st.session_state.user_api_key,
                type="password",
                placeholder="Enter your API key",
                key="api_key_field"
            )
            
            if api_key_input != st.session_state.user_api_key:
                st.session_state.user_api_key = api_key_input
                set_api_key(api_key_input)
                st.cache_data.clear()
                st.rerun()
            
            if st.session_state.user_api_key:
                st.success("Using custom API key")
        
        st.markdown("---")
        st.markdown("### Search Options")
        
        search_type = st.radio(
            "Search by:",
            ["NSN/NIIN", "Part Number"],
            key="search_type_radio"
        )
        
        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
        This application queries the OpenFLIS API to retrieve 
        comprehensive logistics data for military supply items.
        
        **Data Available:**
        - Item identification
        - Management data & pricing
        - Service ownership (MOE Rules)
        - Standardization status
        - Army-specific data
        - Historical records
        """)
        
        st.markdown("---")
        st.markdown("### Quick Tips")
        st.markdown("""
        - Enter full NSN (e.g., 1560-01-162-5517)
        - Or just the NIIN (e.g., 011625517)
        - Part numbers can include dashes
        """)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if search_type == "NSN/NIIN":
            search_input = st.text_input(
                "Enter NSN or NIIN:",
                placeholder="e.g., 1560-01-162-5517 or 011625517",
                key="nsn_input"
            )
        else:
            search_input = st.text_input(
                "Enter Part Number:",
                placeholder="e.g., 39-9918-22",
                key="part_input"
            )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        search_clicked = st.button("🔍 Search", type="primary", use_container_width=True)
    
    if not get_api_key():
        st.warning("Please configure your API key in the sidebar settings to search.")
    
    if search_clicked and search_input:
        if not get_api_key():
            st.error("API Key required. Please enter your API key in the sidebar settings.")
            st.stop()
        with st.spinner("Fetching data from OpenFLIS API..."):
            if search_type == "NSN/NIIN":
                niin, fsc = parse_nsn_input(search_input)
                
                comprehensive_data = cached_get_comprehensive_data(niin)
                overview = build_item_overview(niin, comprehensive_data)
                
                if fsc and not overview.get('fsc'):
                    overview['fsc'] = fsc
                    overview['nsn'] = f"{fsc}-{niin}"
                
                st.session_state.search_results = {
                    'type': 'nsn',
                    'niin': niin,
                    'overview': overview,
                    'comprehensive_data': comprehensive_data
                }
            else:
                part_result = cached_lookup_by_part_number(search_input)
                
                if part_result.get('Matched') and part_result.get('NIIN'):
                    niin = part_result['NIIN']
                    comprehensive_data = cached_get_comprehensive_data(niin)
                    overview = build_item_overview(niin, comprehensive_data)
                    
                    st.session_state.search_results = {
                        'type': 'part',
                        'part_number': search_input,
                        'niin': niin,
                        'overview': overview,
                        'comprehensive_data': comprehensive_data
                    }
                else:
                    st.session_state.search_results = {
                        'type': 'part',
                        'part_number': search_input,
                        'error': 'No matching item found for this part number.'
                    }
        
        st.session_state.last_search = search_input
    
    if st.session_state.search_results:
        results = st.session_state.search_results
        
        if results.get('error'):
            st.error(results['error'])
        else:
            st.success(f"✅ Data retrieved for NIIN: {results['niin']}")
            
            if results['type'] == 'part':
                st.info(f"Part Number '{results['part_number']}' maps to NIIN: {results['niin']}")
            
            overview = results['overview']
            comprehensive_data = results['comprehensive_data']
            
            display_item_overview(overview)
            
            tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
                "💰 Management",
                "📜 MOE Rules",
                "📊 Standardization",
                "🎖️ Army Mgmt",
                "📚 History",
                "🔮 Future",
                "🔧 Raw Data"
            ])
            
            with tab1:
                display_management_data(comprehensive_data.get('management', {}))
            
            with tab2:
                display_moe_rules(comprehensive_data.get('moe_rule', {}))
            
            with tab3:
                display_standardization(comprehensive_data.get('standardization', {}))
            
            with tab4:
                display_army_management(comprehensive_data.get('army_management', {}))
            
            with tab5:
                display_history(comprehensive_data.get('history', {}))
                st.markdown("---")
                display_management_history(comprehensive_data.get('management_history', {}))
            
            with tab6:
                display_management_future(comprehensive_data.get('management_future', {}))
            
            with tab7:
                display_raw_data(comprehensive_data)

if __name__ == "__main__":
    main()
