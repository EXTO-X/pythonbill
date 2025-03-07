import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import glob
import os
from datetime import datetime, timedelta

# Import from our modules
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from utils.analytics_ui import visualize_sales_data  # Corrected import
from utils.bill_operations import (
    generate_bill_number, 
    calculate_total, 
    generate_bill, 
    save_bill, 
    print_bill, 
    export_bill_to_excel
)
from utils.email_utils import send_email
from utils.data import prices, cosmetic_products, grocery_products, drink_products
from utils.ui import (
    set_custom_style,
    display_customer_info_section,
    display_product_selection,
    display_bill_operations_section,
    display_bill_content,
    display_success_message,
    display_error_message
)

# Set page config
st.set_page_config(
    page_title="Grocery Billing System",
    page_icon="🛒",
    layout="wide"
)

# Apply custom styling
set_custom_style()

# Initialize session state
if "billnumber" not in st.session_state:
    st.session_state.billnumber = generate_bill_number()

# Title
st.title("Grocery Billing System")

# Get customer information
customer_name, phone_number = display_customer_info_section()

# Get product selections
cosmetic_items, grocery_items, drink_items = display_product_selection(
    cosmetic_products, grocery_products, drink_products, prices
)

# Bill operations section
bill_op_cols = display_bill_operations_section()

# Calculate button
with bill_op_cols[0]:
    if st.button("Calculate Total", key="calc_button"):
        if not customer_name:
            display_error_message("Please enter customer name")
        elif not phone_number:
            display_error_message("Please enter phone number")
        elif not any(qty > 0 for qty in {**cosmetic_items, **grocery_items, **drink_items}.values()):
            display_error_message("Please select at least one product")
        else:
            # Calculate totals
            totals = calculate_total(cosmetic_items, grocery_items, drink_items, prices)
            st.session_state.totals = totals
            
            # Generate bill
            bill_content = generate_bill(
                customer_name, 
                phone_number, 
                st.session_state.billnumber, 
                cosmetic_items, 
                grocery_items, 
                drink_items, 
                totals,
                prices
            )
            st.session_state.bill_content = bill_content
            
            # Display success message
            display_success_message("Bill calculated successfully!")

# Add the rest of your bill operation buttons (Save, Print, Email, Export)
with bill_op_cols[1]:
    if st.button("Save Bill", key="save_button"):
        if "bill_content" in st.session_state:
            result = save_bill(st.session_state.bill_content, st.session_state.billnumber)
            display_success_message(result)
        else:
            display_error_message("Please calculate the bill first")
with bill_op_cols[2]:
    if st.button("Print Bill", key="print_button"):
        if "bill_content" in st.session_state:
            result = print_bill(st.session_state.bill_content)
            if result.startswith("Error") or "only available" in result:
                display_error_message(result)
            else:
                display_success_message(result)
        else:
            display_error_message("Please calculate the bill first")
with bill_op_cols[3]:
    if st.button("Email Bill", key="email_button", type="primary"):
        if "bill_content" in st.session_state:
            st.session_state.show_email_form = True
        else:
            display_error_message("Please calculate the bill first")

# Add a new column for Export to Excel button
with st.container():
    if st.button("Export to Excel", key="excel_button"):
        if "totals" in st.session_state:
            file_path = export_bill_to_excel(
                customer_name,
                phone_number,
                st.session_state.billnumber,
                cosmetic_items,
                grocery_items,
                drink_items,
                st.session_state.totals,
                prices
            )
            display_success_message(f"Bill exported to {file_path}")
        else:
            display_error_message("Please calculate the bill first")

# Email form section
if "show_email_form" in st.session_state and st.session_state.show_email_form:
    st.markdown("## Send Bill via Email")
    
    email_col1, email_col2 = st.columns(2)
    
    with email_col1:
        sender_email = st.text_input("Sender Email", key="sender_email")
        sender_password = st.text_input("Password", type="password", key="sender_password")
        
    with email_col2:
        receiver_email = st.text_input("Receiver Email", key="receiver_email")
        
    email_action_col1, email_action_col2 = st.columns(2)
    with email_action_col1:
        if st.button("Send Email", key="send_email_button"):
            if sender_email and sender_password and receiver_email:
                if "bill_content" in st.session_state:
                    try:
                        if send_email(sender_email, sender_password, receiver_email, st.session_state.bill_content):
                            display_success_message("Email sent successfully!")
                            st.session_state.show_email_form = False
                        else:
                            display_error_message("Failed to send email. Please check your credentials.")
                    except Exception as e:
                        display_error_message(f"Error sending email: {str(e)}")
                else:
                    display_error_message("No bill content to send. Calculate total first.")
            else:
                display_error_message("Please fill all email fields")
    
    with email_action_col2:
        if st.button("Cancel", key="cancel_email_button"):
            st.session_state.show_email_form = False
            st.rerun()
# Display bill content if available
if "bill_content" in st.session_state:
    display_bill_content(st.session_state.bill_content)

# Add a section for analytics
if st.sidebar.button("View Sales Analytics", type="primary"):
    # Find all Excel files in the bills directory
    excel_files = glob.glob("bills/*.xlsx")
    if excel_files:
        st.success(f"Found {len(excel_files)} Excel files for analysis")
        # Create a container for analytics
        with st.container():
            st.markdown("## Sales Analytics")
            try:
                # Pass all Excel files to the visualization function
                visualize_sales_data(excel_files)
            except Exception as e:
                st.error(f"Error in analytics visualization: {str(e)}")
                st.info("Please check the format of your Excel files or try exporting new bills.")
    else:
        display_error_message("No Excel files found. Please export some bills to Excel first.")
        st.info("To generate analytics data, calculate a bill and click 'Export to Excel'")
        
        # Create a sample bill for demonstration
        if st.button("Create Sample Data for Analytics"):
            try:
                # Create bills directory if it doesn't exist
                os.makedirs("bills", exist_ok=True)
                
                # Create a sample dataframe with required columns
                sample_data = {
                    'Date': [datetime.now() - timedelta(days=i) for i in range(10)],
                    'Bill Number': [f"BILL{i+1000}" for i in range(10)],
                    'Customer Name': ['Sample Customer'] * 10,
                    'Phone': ['1234567890'] * 10,
                    'Product': ['Rice', 'Dal', 'Tea', 'Bath Soap', 'Face Cream', 'Red Bull', 
                               'Hurricane', 'Oil', 'Wheat', 'Sugar'],
                    'Category': ['Groceries', 'Groceries', 'Groceries', 'Cosmetics', 'Cosmetics', 
                                'Drinks', 'Drinks', 'Groceries', 'Groceries', 'Groceries'],
                    'Quantity': [i+1 for i in range(10)],
                    'Price': [50, 100, 120, 45, 85, 110, 95, 200, 40, 60],
                    'Total': [50*(i+1) for i in range(10)]
                }
                
                df = pd.DataFrame(sample_data)
                
                # Save to Excel
                sample_file = "bills/sample_data.xlsx"
                df.to_excel(sample_file, index=False)
                
                display_success_message(f"Sample data created at {sample_file}")
                st.info("Now click 'View Sales Analytics' again to see the visualization")
            except Exception as e:
                display_error_message(f"Error creating sample data: {str(e)}")

# Add a search bill section
st.sidebar.markdown("---")
st.sidebar.markdown("## Search Bills")
search_option = st.sidebar.radio("Search by:", ["Bill Number", "Customer Name", "Date"])

if search_option == "Bill Number":
    # Get all bill files - fix the pattern to match both formats
    bill_files = glob.glob("bills/*.txt")  # More general pattern to catch all text files
    bill_numbers = [os.path.basename(file).replace(".txt", "") for file in bill_files]
    
    if bill_numbers:
        selected_bill = st.sidebar.selectbox("Select Bill Number:", bill_numbers)
        if st.sidebar.button("View Bill", key="view_bill_by_number"):  # Added unique key
            bill_path = f"bills/{selected_bill}.txt"
            try:
                with open(bill_path, "r", encoding="utf-8") as f:
                    bill_content = f.read()
                st.session_state.bill_content = bill_content
                display_success_message(f"Loaded bill: {selected_bill}")
            except Exception as e:
                display_error_message(f"Error loading bill: {str(e)}")
    else:
        st.sidebar.info("No bills found. Please save a bill first.")

elif search_option == "Customer Name":
    # Get all bill files
    bill_files = glob.glob("bills/*.txt")  # More general pattern
    customer_names = []
    
    for file in bill_files:
        try:
            with open(file, "r", encoding="utf-8") as f:
                content = f.read()
                # Extract customer name from bill content
                for line in content.split("\n"):
                    if "Customer Name:" in line:
                        name = line.split("Customer Name:")[1].strip()
                        customer_names.append((name, file))
                        break
        except Exception as e:
            st.sidebar.error(f"Error reading {file}: {str(e)}")
    
    if customer_names:
        # Get unique names
        unique_names = list(set([name for name, _ in customer_names]))
        selected_name = st.sidebar.selectbox("Select Customer:", unique_names)
        
        # Find bills for this customer
        customer_bills = [file for name, file in customer_names if name == selected_name]
        
        if customer_bills:
            selected_bill = st.sidebar.selectbox(
                "Select Bill:", 
                [os.path.basename(file) for file in customer_bills]
            )
            
            if st.sidebar.button("View Bill", key="view_bill_by_customer"):  # Added unique key
                try:
                    with open(os.path.join("bills", selected_bill), "r", encoding="utf-8") as f:
                        bill_content = f.read()
                    st.session_state.bill_content = bill_content
                    display_success_message(f"Loaded bill for {selected_name}")
                except Exception as e:
                    display_error_message(f"Error loading bill: {str(e)}")
        else:
            st.sidebar.info(f"No bills found for {selected_name}.")
    else:
        st.sidebar.info("No customer bills found. Please save a bill first.")

elif search_option == "Date":
    # Get all bill files
    bill_files = glob.glob("bills/*.txt")  # More general pattern
    bill_dates = []
    
    for file in bill_files:
        try:
            with open(file, "r", encoding="utf-8") as f:
                content = f.read()
                # Extract date from bill content
                for line in content.split("\n"):
                    if "Date:" in line:
                        date_str = line.split("Date:")[1].strip()
                        try:
                            date = datetime.strptime(date_str, "%d-%m-%Y %H:%M:%S").date()
                            bill_dates.append((date, file))
                            break
                        except:
                            # Try alternative date format if the first one fails
                            try:
                                date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S").date()
                                bill_dates.append((date, file))
                                break
                            except:
                                pass
        except Exception as e:
            st.sidebar.error(f"Error reading {file}: {str(e)}")
    
    if bill_dates:
        # Sort dates
        bill_dates.sort(reverse=True)
        unique_dates = sorted(list(set([date for date, _ in bill_dates])), reverse=True)
        
        selected_date = st.sidebar.selectbox(
            "Select Date:", 
            [date.strftime("%d-%m-%Y") for date in unique_dates]
        )
        
        # Find bills for this date
        date_obj = datetime.strptime(selected_date, "%d-%m-%Y").date()
        date_bills = [file for date, file in bill_dates if date == date_obj]
        
        if date_bills:
            selected_bill = st.sidebar.selectbox(
                "Select Bill:", 
                [os.path.basename(file) for file in date_bills]
            )
            
            if st.sidebar.button("View Bill", key="view_bill_by_date"):  # Added unique key
                try:
                    with open(os.path.join("bills", selected_bill), "r", encoding="utf-8") as f:
                        bill_content = f.read()
                    st.session_state.bill_content = bill_content
                    display_success_message(f"Loaded bill from {selected_date}")
                except Exception as e:
                    display_error_message(f"Error loading bill: {str(e)}")
        else:
            st.sidebar.info(f"No bills found for {selected_date}.")
    else:
        st.sidebar.info("No dated bills found. Please save a bill first.")

# Reset button to clear the form
st.sidebar.markdown("---")
if st.sidebar.button("New Bill"):
    # Generate a new bill number
    st.session_state.billnumber = generate_bill_number()
    # Clear session state
    if "bill_content" in st.session_state:
        del st.session_state.bill_content
    if "totals" in st.session_state:
        del st.session_state.totals
    # Rerun the app to clear inputs
    st.rerun()
