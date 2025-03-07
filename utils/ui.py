import streamlit as st

from .analytics_ui import visualize_sales_data

def set_custom_style():
    """Apply custom CSS styling to the Streamlit app."""
    st.markdown("""
    <style>
        .section-header {
            font-size: 24px;
            font-weight: bold;
            margin-top: 20px;
            margin-bottom: 10px;
            padding: 5px;
            border-bottom: 2px solid #4CAF50;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 24px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            background-color: #F0F2F6;
            border-radius: 4px 4px 0px 0px;
            gap: 1px;
            padding-top: 10px;
            padding-bottom: 10px;
        }
        .stTabs [aria-selected="true"] {
            background-color: #4CAF50;
            color: white;
        }
    </style>
    """, unsafe_allow_html=True)

def display_customer_info_section():
    """Display the customer information section and return the input values."""
    st.markdown('<div class="section-header">Customer Information</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        customer_name = st.text_input("Customer Name")
    with col2:
        phone_number = st.text_input("Phone Number")
    
    return customer_name, phone_number

def display_product_selection(cosmetic_products, grocery_products, drink_products, prices):
    """Display product selection section with variants"""
    st.markdown('<div class="section-header">Product Selection</div>', unsafe_allow_html=True)
    
    # Create tabs for different product categories
    tabs = st.tabs(["Cosmetics", "Groceries", "Drinks"])
    
    # Initialize dictionaries to store selected quantities
    cosmetic_items = {}
    grocery_items = {}
    drink_items = {}
    
    # Cosmetics tab
    with tabs[0]:
        st.markdown("### Cosmetic Products")
        
        # Create an expander for each product type
        for product_type, variants in cosmetic_products.items():
            with st.expander(f"{product_type}"):
                # Create columns for each variant
                cols = st.columns(len(variants))
                
                # Display each variant in its own column
                for i, variant in enumerate(variants):
                    with cols[i]:
                        st.markdown(f"**{variant['name']}**")
                        st.markdown(f"Price: ₹{variant['price']}")
                        qty = st.number_input(
                            "Quantity",
                            min_value=0,
                            value=0,
                            step=1,
                            key=f"cosmetic_{variant['name']}"
                        )
                        cosmetic_items[variant['name']] = qty
    
    # Groceries tab
    with tabs[1]:
        st.markdown("### Grocery Products")
        
        # Create an expander for each product type
        for product_type, variants in grocery_products.items():
            with st.expander(f"{product_type}"):
                # Create columns for each variant
                cols = st.columns(len(variants))
                
                # Display each variant in its own column
                for i, variant in enumerate(variants):
                    with cols[i]:
                        st.markdown(f"**{variant['name']}**")
                        st.markdown(f"Price: ₹{variant['price']}")
                        qty = st.number_input(
                            "Quantity",
                            min_value=0,
                            value=0,
                            step=1,
                            key=f"grocery_{variant['name']}"
                        )
                        grocery_items[variant['name']] = qty
    
    # Drinks tab
    with tabs[2]:
        st.markdown("### Drink Products")
        
        # Create an expander for each product type
        for product_type, variants in drink_products.items():
            with st.expander(f"{product_type}"):
                # Create columns for each variant
                cols = st.columns(len(variants))
                
                # Display each variant in its own column
                for i, variant in enumerate(variants):
                    with cols[i]:
                        st.markdown(f"**{variant['name']}**")
                        st.markdown(f"Price: ₹{variant['price']}")
                        qty = st.number_input(
                            "Quantity",
                            min_value=0,
                            value=0,
                            step=1,
                            key=f"drink_{variant['name']}"
                        )
                        drink_items[variant['name']] = qty
    
    return cosmetic_items, grocery_items, drink_items

def display_bill_operations_section():
    """Display the bill operations section with buttons."""
    st.markdown('<div class="section-header">Bill Operations</div>', unsafe_allow_html=True)
    return st.columns(4)

def display_bill_content(bill_content):
    """Display the bill content in a text area."""
    st.markdown('<div class="section-header">Bill Preview</div>', unsafe_allow_html=True)
    
    # Display the bill content in a text area
    st.text_area("Bill", bill_content, height=400)
    # Removed duplicate text_area line
def display_success_message(message):
    """Display a success message."""
    st.success(message)

def display_error_message(message):
    """Display an error message."""
    st.error(message)

def display_data_analysis_section(excel_file_path):
    """Display the data analysis section."""
    visualize_sales_data(excel_file_path)