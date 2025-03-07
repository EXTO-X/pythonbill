import os
import random
import datetime
from datetime import datetime  # Add this specific import
import streamlit as st
import pandas as pd
# Import Windows-specific modules conditionally
import platform
if platform.system() == 'Windows':
    import win32print
    import win32api
import tempfile
import threading
import time
import subprocess

# Remove duplicate imports
# import os
# import random
# import datetime
# from datetime import datetime
# import streamlit as st
# import pandas as pd
# import win32print
# import win32api

# Prices dictionary
prices = {
    # Cosmetics
    "Bath Soap": 25,
    "Face Cream": 80,
    "Face Wash": 120,
    "Hair Spray": 180,
    "Hair Gel": 140,
    "Body Lotion": 180,
    # Groceries
    "Rice": 50,
    "Dal": 100,
    "Oil": 120,
    "Wheat": 40,
    "Sugar": 45,
    "Tea": 140,
    # Energy Drinks
    "Red Bull": 120,
    "Hurricane": 90,
    "Blue Bull": 100,
    "Ocean": 85,
    "Monster": 110,
    "Coca Cola": 60
}

def generate_bill_number():
    # Generate a random bill number
    return f"BILL{random.randint(10000, 99999)}"

def calculate_total(cosmetic_items, grocery_items, drink_items, prices):
    # Calculate totals for each category
    cosmetic_total = sum(prices[item] * qty for item, qty in cosmetic_items.items() if qty > 0)
    grocery_total = sum(prices[item] * qty for item, qty in grocery_items.items() if qty > 0)
    drink_total = sum(prices[item] * qty for item, qty in drink_items.items() if qty > 0)
    
    # Calculate tax
    cosmetic_tax = cosmetic_total * 0.12
    grocery_tax = grocery_total * 0.05
    drink_tax = drink_total * 0.18
    
    # Calculate final totals
    cosmetic_final = cosmetic_total + cosmetic_tax
    grocery_final = grocery_total + grocery_tax
    drink_final = drink_total + drink_tax
    
    # Calculate grand total
    grand_total = cosmetic_final + grocery_final + drink_final
    
    return {
        "cosmetic_total": cosmetic_total,
        "grocery_total": grocery_total,
        "drink_total": drink_total,
        "cosmetic_tax": cosmetic_tax,
        "grocery_tax": grocery_tax,
        "drink_tax": drink_tax,
        "cosmetic_final": cosmetic_final,
        "grocery_final": grocery_final,
        "drink_final": drink_final,
        "grand_total": grand_total
    }
def generate_bill(customer_name, phone_number, bill_number, cosmetic_items, grocery_items, drink_items, totals, prices):
    # Get current time
    current_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    
    # Create bill header
    bill = f"""
{'*' * 70}
                      GROCERY BILLING SYSTEM
{'*' * 70}
Bill Number: {bill_number}
Customer Name: {customer_name}
Phone Number: {phone_number}
Date: {current_time}
{'=' * 70}
Product                 Quantity         Price         Total
{'=' * 70}
"""
    
    # Add cosmetic items to bill
    if any(qty > 0 for qty in cosmetic_items.values()):
        bill += "COSMETICS\n"
        for item, qty in cosmetic_items.items():
            if qty > 0:
                price = prices[item]
                total = price * qty
                bill += f"{item:<25}{qty:<15}{price:<15}{total}\n"
        bill += f"Cosmetic Tax: {totals['cosmetic_tax']:.2f}\n"
        bill += f"Cosmetic Total: {totals['cosmetic_final']:.2f}\n\n"
    
    # Add grocery items to bill
    if any(qty > 0 for qty in grocery_items.values()):
        bill += "GROCERIES\n"
        for item, qty in grocery_items.items():
            if qty > 0:
                price = prices[item]
                total = price * qty
                bill += f"{item:<25}{qty:<15}{price:<15}{total}\n"
        bill += f"Grocery Tax: {totals['grocery_tax']:.2f}\n"
        bill += f"Grocery Total: {totals['grocery_final']:.2f}\n\n"
    
    # Add drink items to bill
    if any(qty > 0 for qty in drink_items.values()):
        bill += "DRINKS\n"  # Changed from "ENERGY DRINKS" to "DRINKS" for consistency
        for item, qty in drink_items.items():
            if qty > 0:
                price = prices[item]
                total = price * qty
                bill += f"{item:<25}{qty:<15}{price:<15}{total}\n"
        bill += f"Drink Tax: {totals['drink_tax']:.2f}\n"
        bill += f"Drink Total: {totals['drink_final']:.2f}\n\n"
    
    # Add grand total
    bill += f"{'=' * 70}\n"
    bill += f"Grand Total: ₹{totals['grand_total']:.2f}\n"
    bill += f"{'=' * 70}\n"
    bill += f"Thank you for shopping with us!\n"
    
    return bill
def save_bill(bill_content, bill_number):
    # Create bills directory if it doesn't exist
    if not os.path.exists("bills"):
        os.makedirs("bills")
    
    # Save bill to text file with UTF-8 encoding
    file_path = f"bills/{bill_number}.txt"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(bill_content)
    
    return f"Bill saved to {file_path}"
# Then modify your printing function to check the platform
def print_bill(bill_content):
    """Print the bill to the default printer."""
    if platform.system() != 'Windows':
        return "Printing is only available on Windows systems."
    
    try:
        # Windows-specific printing code
        filename = tempfile.mktemp(".txt")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(bill_content)
        
        win32api.ShellExecute(
            0,
            "print",
            filename,
            f'/d:"{win32print.GetDefaultPrinter()}"',
            ".",
            0
        )
        # Wait a moment to ensure the print job is sent
        time.sleep(1)
        return "Bill sent to printer successfully!"
    except Exception as e:
        return f"Error printing bill: {str(e)}"
def export_bill_to_excel(customer_name, phone_number, bill_number, cosmetic_items, grocery_items, drink_items, totals, prices):
    """Export bill to Excel file"""
    # Create bills directory if it doesn't exist
    os.makedirs("bills", exist_ok=True)
    
    # Current date and time
    now = datetime.now()
    date_str = now.strftime("%d-%m-%Y %H:%M:%S")
    
    # Create a list to store all items
    all_items = []
    
    # Add cosmetic items
    for item, qty in cosmetic_items.items():
        if qty > 0:
            price = prices.get(item, 0)
            all_items.append({
                'Date': now,
                'Bill Number': bill_number,
                'Customer Name': customer_name,
                'Phone': phone_number,
                'Category': 'Cosmetics',
                'Product': item,
                'Quantity': qty,
                'Price': price,
                'Total': qty * price
            })
    
    # Add grocery items
    for item, qty in grocery_items.items():
        if qty > 0:
            price = prices.get(item, 0)
            all_items.append({
                'Date': now,
                'Bill Number': bill_number,
                'Customer Name': customer_name,
                'Phone': phone_number,
                'Category': 'Groceries',
                'Product': item,
                'Quantity': qty,
                'Price': price,
                'Total': qty * price
            })
    
    # Add drink items
    for item, qty in drink_items.items():
        if qty > 0:
            price = prices.get(item, 0)
            all_items.append({
                'Date': now,
                'Bill Number': bill_number,
                'Customer Name': customer_name,
                'Phone': phone_number,
                'Category': 'Drinks',
                'Product': item,
                'Quantity': qty,
                'Price': price,
                'Total': qty * price
            })
    
    # Create DataFrame
    df = pd.DataFrame(all_items)
    
    # Save to Excel
    file_path = f"bills/{bill_number}.xlsx"
    df.to_excel(file_path, index=False)
    
    return file_path
