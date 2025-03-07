# Import the new function
from utils.bill_storage import save_bill_to_master

# In your bill generation function, after creating the bill DataFrame:
def generate_bill(items, customer_info, bill_number, date):
    # Your existing code to create the bill DataFrame
    # ...
    
    # Save to individual bill file (if you still want this)
    bill_file_path = f"bills/bill_{bill_number}_{date.strftime('%Y%m%d')}.xlsx"
    bill_df.to_excel(bill_file_path, index=False)
    
    # Also save to the master file
    master_file_path = save_bill_to_master(bill_df)
    
    return bill_file_path, master_file_path