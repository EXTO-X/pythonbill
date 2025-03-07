import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io
from datetime import datetime
import os
# Removed seaborn and matplotlib imports
# Removed streamlit_mito import

def visualize_sales_data(excel_files=None):
    """Visualize sales data based on date, week, month, and year."""
    st.markdown('<div class="section-header">Sales Data Visualization</div>', unsafe_allow_html=True)
    
    # If no files are provided, use the master file
    if excel_files is None:
        master_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                       'data', 'master_bills.xlsx')
        if os.path.exists(master_file_path):
            excel_files = master_file_path
        else:
            st.error("Master bill file not found. Please generate some bills first.")
            return
    
    # Check if excel_files is a list or a single file path
    if not isinstance(excel_files, list):
        excel_files = [excel_files]
    
    # Load data from a single Excel file or combine multiple if needed
    all_data = []
    for file in excel_files:
        try:
            # Read the Excel file - assuming all bills are in a single sheet
            df = pd.read_excel(file)
            
            # Skip the summary row (last row) if it exists
            if not df.empty and 'Category' in df.columns:
                df = df[df['Category'] != 'TOTAL']
                # Standardize all category names to title case
                if df['Category'].dtype == 'object':  # Only apply string methods if column is string type
                    df['Category'] = df['Category'].str.title()
                all_data.append(df)
            else:
                st.warning(f"File {file} is missing required columns. Required columns: Category, Date")
        except Exception as e:
            st.warning(f"Could not read {file}: {e}")
    
    if not all_data:
        st.warning("No valid data found in the Excel files.")
        return
    
    # Combine all data
    sales_data = pd.concat(all_data, ignore_index=True)
    
    # Ensure the Date column is in datetime format
    if 'Date' not in sales_data.columns:
        st.error("The Excel files do not contain a 'Date' column.")
        return
    
    # Convert Date column to datetime and handle any conversion errors
    sales_data['Date'] = pd.to_datetime(sales_data['Date'], errors='coerce')
    sales_data.dropna(subset=['Date'], inplace=True)  # Drop rows with invalid dates
    
    # Add additional time-based columns with proper error handling
    try:
        sales_data['Week'] = sales_data['Date'].dt.isocalendar().week
        sales_data['Month'] = sales_data['Date'].dt.strftime('%Y-%m')
        sales_data['MonthName'] = sales_data['Date'].dt.strftime('%B')
        sales_data['Year'] = sales_data['Date'].dt.year
        sales_data['Day'] = sales_data['Date'].dt.day_name()
    except Exception as e:
        st.error(f"Error processing date columns: {e}")
        return
    
    # Store filter state in session state to persist between reruns
    if 'filter_expanded' not in st.session_state:
        st.session_state.filter_expanded = True
    
    # Create a copy of the original data for filtering
    filtered_data = sales_data.copy()
    
    # Create a container for filters that stays open
    with st.expander("Filter Options", expanded=st.session_state.filter_expanded):
        col1, col2 = st.columns(2)
        with col1:
            # Date range filter
            min_date = sales_data['Date'].min().date()
            max_date = sales_data['Date'].max().date()
            # Use session state to maintain selected dates
            if 'start_date' not in st.session_state:
                st.session_state.start_date = min_date
            if 'end_date' not in st.session_state:
                st.session_state.end_date = max_date
                
            date_range = st.date_input(
                "Select Date Range",
                value=(st.session_state.start_date, st.session_state.end_date),
                min_value=min_date,
                max_value=max_date,
                key="date_range_filter"
            )
            if len(date_range) == 2:
                start_date, end_date = date_range
                st.session_state.start_date = start_date
                st.session_state.end_date = end_date
                filtered_data = filtered_data[(filtered_data['Date'].dt.date >= start_date) & 
                                           (filtered_data['Date'].dt.date <= end_date)]
        with col2:
            # Category filter - use session state to maintain selection
            if 'Category' in sales_data.columns:
                # Get all unique categories from the original data
                all_categories = sorted(sales_data['Category'].unique().tolist())
                categories = ['All'] + all_categories
                
                if 'selected_category' not in st.session_state:
                    st.session_state.selected_category = 'All'
                
                # Make sure the selected category is in the list
                if st.session_state.selected_category not in categories:
                    st.session_state.selected_category = 'All'
                
                selected_category = st.selectbox(
                    "Select Category",
                    categories,
                    index=categories.index(st.session_state.selected_category),
                    key="category_filter"
                )
                
                st.session_state.selected_category = selected_category
                
                if selected_category != 'All':
                    filtered_data = filtered_data[filtered_data['Category'] == selected_category]
            
            # Product filter - use session state to maintain selection
            if 'Product' in sales_data.columns:
                # Get all unique products from the filtered data based on category selection
                if 'selected_category' in st.session_state and st.session_state.selected_category != 'All':
                    available_products = filtered_data['Product'].unique().tolist()
                else:
                    available_products = sales_data['Product'].unique().tolist()
                
                available_products = sorted(available_products)
                products = ['All'] + available_products
                
                if 'selected_product' not in st.session_state:
                    st.session_state.selected_product = 'All'
                
                # Make sure the selected product is in the list
                if st.session_state.selected_product not in products:
                    st.session_state.selected_product = 'All'
                
                selected_product = st.selectbox(
                    "Select Product",
                    products,
                    index=products.index(st.session_state.selected_product),
                    key="product_filter"
                )
                
                st.session_state.selected_product = selected_product
                
                if selected_product != 'All':
                    filtered_data = filtered_data[filtered_data['Product'] == selected_product]
    
    # Add a button to reset filters
    if st.button("Reset Filters"):
        st.session_state.selected_category = 'All'
        st.session_state.selected_product = 'All'
        st.session_state.start_date = min_date
        st.session_state.end_date = max_date
        st.experimental_rerun()
    
    # Use the filtered data for the rest of the application
    sales_data = filtered_data
    
    # Check if filtered data is empty
    if sales_data.empty:
        st.warning("No data available for the selected filters.")
        return
    
    # Display summary metrics
    st.subheader("Sales Summary")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Sales", f"₹{sales_data['Total'].sum():.2f}")
    with col2:
        st.metric("Total Items Sold", f"{sales_data['Quantity'].sum()}")
    with col3:
        st.metric("Average Sale Value", f"₹{sales_data['Total'].mean():.2f}")
    with col4:
        st.metric("Number of Transactions", f"{sales_data['Bill Number'].nunique()}")
    
    # Visualization section
    st.subheader("Sales Visualizations")
    
    # Create tabs for different visualizations
    viz_tabs = st.tabs(["Sales by Category", "Sales Trends", "Product Analysis"])
    
    # Sales by Category tab
    with viz_tabs[0]:
        st.markdown("### Sales by Category")
        
        # Pie chart for category distribution using Plotly
        category_sales = sales_data.groupby('Category')['Total'].sum().reset_index()
        
        fig = px.pie(
            category_sales, 
            values='Total', 
            names='Category', 
            title='Sales by Category',
            hover_data=['Total'],
            labels={'Total': 'Sales Amount (₹)'},
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Arial"
            )
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Bar chart for category sales using Plotly
        fig = px.bar(
            category_sales, 
            x='Category', 
            y='Total', 
            title='Total Sales by Category',
            labels={'Total': 'Sales Amount (₹)', 'Category': 'Product Category'},
            color='Category',
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig.update_layout(
            xaxis_tickangle=-45,
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Arial"
            )
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Sales Trends tab
    with viz_tabs[1]:
        st.markdown("### Sales Trends")
        
        # Time series plot using Plotly
        time_grouping = st.selectbox(
            "Group By",
            ["Day", "Week", "Month"],
            key="time_grouping"
        )
        
        if time_grouping == "Day":
            time_data = sales_data.groupby(sales_data['Date'].dt.date)['Total'].sum().reset_index()
            x_label = 'Date'
        elif time_grouping == "Week":
            time_data = sales_data.groupby(['Year', 'Week'])['Total'].sum().reset_index()
            time_data['Period'] = time_data['Year'].astype(str) + '-W' + time_data['Week'].astype(str)
            x_label = 'Period'
        else:  # Month
            time_data = sales_data.groupby('Month')['Total'].sum().reset_index()
            x_label = 'Month'
        
        # Create interactive line plot with Plotly
        if x_label == 'Period':
            fig = px.line(
                time_data, 
                x='Period', 
                y='Total', 
                title=f'Sales Trend by {time_grouping}',
                markers=True,
                labels={'Total': 'Sales Amount (₹)', 'Period': 'Time Period'},
                line_shape='spline',
                render_mode='svg'
            )
        else:
            fig = px.line(
                time_data, 
                x=x_label, 
                y='Total', 
                title=f'Sales Trend by {time_grouping}',
                markers=True,
                labels={'Total': 'Sales Amount (₹)', x_label: f'{time_grouping}'},
                line_shape='spline',
                render_mode='svg'
            )
        
        fig.update_traces(
            line=dict(width=3),
            marker=dict(size=8)
        )
        fig.update_layout(
            xaxis_tickangle=-45 if x_label != 'Date' else 0,
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Arial"
            ),
            hovermode="x unified"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Add a bar chart showing the same data
        if x_label == 'Period':
            fig = px.bar(
                time_data,
                x='Period',
                y='Total',
                title=f'Sales by {time_grouping}',
                labels={'Total': 'Sales Amount (₹)', 'Period': 'Time Period'},
                color_discrete_sequence=['#1f77b4']
            )
        else:
            fig = px.bar(
                time_data,
                x=x_label,
                y='Total',
                title=f'Sales by {time_grouping}',
                labels={'Total': 'Sales Amount (₹)', x_label: f'{time_grouping}'},
                color_discrete_sequence=['#1f77b4']
            )
        
        fig.update_layout(
            xaxis_tickangle=-45 if x_label != 'Date' else 0,
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Arial"
            )
        )
        st.plotly_chart(fig, use_container_width=True)
    # Product Analysis tab (continued)
    with viz_tabs[2]:
        # Add product performance over time
        if not sales_data.empty and 'Product' in sales_data.columns and sales_data['Product'].nunique() > 0:
            st.markdown("### Product Performance Over Time")
            
            # Select a specific product to analyze
            available_products = sorted(sales_data['Product'].unique().tolist())
            if available_products:
                selected_product_analysis = st.selectbox(
                    "Select Product for Time Analysis",
                    available_products,
                    key="product_time_analysis"
                )
                
                # Filter data for the selected product
                product_time_data = sales_data[sales_data['Product'] == selected_product_analysis]
                
                # Group by time period
                time_period = st.radio(
                    "Select Time Period",
                    ["Day", "Week", "Month"],
                    horizontal=True,
                    key="product_time_period"
                )
                
                if time_period == "Day":
                    product_time_grouped = product_time_data.groupby(product_time_data['Date'].dt.date)['Quantity'].sum().reset_index()
                    x_axis = 'Date'
                elif time_period == "Week":
                    product_time_grouped = product_time_data.groupby(['Year', 'Week'])[['Quantity', 'Total']].sum().reset_index()
                    product_time_grouped['Period'] = product_time_grouped['Year'].astype(str) + '-W' + product_time_grouped['Week'].astype(str)
                    x_axis = 'Period'
                else:  # Month
                    product_time_grouped = product_time_data.groupby('Month')[['Quantity', 'Total']].sum().reset_index()
                    x_axis = 'Month'
                
                # Create visualization
                if not product_time_grouped.empty:
                    # Create a two-line chart showing quantity and sales amount
                    fig = go.Figure()
                    
                    # Add quantity line
                    fig.add_trace(go.Scatter(
                        x=product_time_grouped[x_axis],
                        y=product_time_grouped['Quantity'],
                        name='Quantity Sold',
                        line=dict(color='#1f77b4', width=3),
                        mode='lines+markers'
                    ))
                    
                    # Add sales amount line if available
                    if 'Total' in product_time_grouped.columns:
                        fig.add_trace(go.Scatter(
                            x=product_time_grouped[x_axis],
                            y=product_time_grouped['Total'],
                            name='Sales Amount (₹)',
                            line=dict(color='#ff7f0e', width=3),
                            mode='lines+markers',
                            yaxis='y2'
                        ))
                    # Update layout for dual y-axis
                    fig.update_layout(
                        title=f'{selected_product_analysis} Performance by {time_period}',
                        xaxis=dict(title=time_period),
                        yaxis=dict(
                            title='Quantity Sold', 
                            title_font=dict(color='#1f77b4'),  # Changed from titlefont to title_font
                            tickfont=dict(color='#1f77b4')
                        ),
                        yaxis2=dict(
                            title='Sales Amount (₹)', 
                            title_font=dict(color='#ff7f0e'),  # Changed from titlefont to title_font
                            tickfont=dict(color='#ff7f0e'), 
                            anchor='x', 
                            overlaying='y', 
                            side='right'
                        ),
                        hovermode='x unified',
                        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
                        margin=dict(l=60, r=60, t=50, b=50)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info(f"No time-series data available for {selected_product_analysis}.")
    
    # Add a new tab for customer analysis if customer data is available
    if 'Customer' in sales_data.columns:
        customer_tab = st.expander("Customer Analysis", expanded=False)
        with customer_tab:
            st.markdown("### Customer Analysis")
            
            # Top customers by sales
            top_customers = sales_data.groupby('Customer')['Total'].sum().reset_index()
            top_customers = top_customers.sort_values('Total', ascending=False).head(10)
            
            if not top_customers.empty:
                fig = px.bar(
                    top_customers,
                    x='Customer',
                    y='Total',
                    title='Top 10 Customers by Sales',
                    labels={'Total': 'Sales Amount (₹)', 'Customer': 'Customer Name'},
                    color='Total',
                    color_continuous_scale='Viridis'
                )
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
            
            # Customer purchase frequency
            if 'Bill Number' in sales_data.columns:
                customer_frequency = sales_data.groupby('Customer')['Bill Number'].nunique().reset_index()
                customer_frequency.columns = ['Customer', 'Purchase Frequency']
                customer_frequency = customer_frequency.sort_values('Purchase Frequency', ascending=False).head(10)
                
                if not customer_frequency.empty:
                    fig = px.bar(
                        customer_frequency,
                        x='Customer',
                        y='Purchase Frequency',
                        title='Top 10 Customers by Purchase Frequency',
                        labels={'Purchase Frequency': 'Number of Purchases', 'Customer': 'Customer Name'},
                        color='Purchase Frequency',
                        color_continuous_scale='Viridis'
                    )
                    fig.update_layout(xaxis_tickangle=-45)
                    st.plotly_chart(fig, use_container_width=True)
    
    # Add a new tab for inventory analysis
    inventory_tab = st.expander("Inventory Analysis", expanded=False)
    with inventory_tab:
        st.markdown("### Inventory Analysis")
        
        if 'Product' in sales_data.columns and 'Quantity' in sales_data.columns:
            # Calculate total quantity sold per product
            product_quantity = sales_data.groupby('Product')['Quantity'].sum().reset_index()
            product_quantity = product_quantity.sort_values('Quantity', ascending=True)  # Ascending to show low stock at top
            
            # Display as a horizontal bar chart
            fig = px.bar(
                product_quantity,
                y='Product',
                x='Quantity',
                orientation='h',
                title='Product Quantities Sold',
                labels={'Quantity': 'Units Sold', 'Product': 'Product Name'},
                color='Quantity',
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Add a table view of the inventory data
            st.markdown("### Inventory Data Table")
            
            # Create a more detailed inventory table
            if 'Category' in sales_data.columns:
                inventory_table = sales_data.groupby(['Category', 'Product'])['Quantity'].sum().reset_index()
                inventory_table = inventory_table.sort_values(['Category', 'Quantity'], ascending=[True, False])
                
                # Add a search box for the inventory table
                search_term = st.text_input("Search Products", "")
                if search_term:
                    inventory_table = inventory_table[inventory_table['Product'].str.contains(search_term, case=False)]
                
                st.dataframe(inventory_table, use_container_width=True)
            else:
                inventory_table = product_quantity.sort_values('Quantity', ascending=False)
                st.dataframe(inventory_table, use_container_width=True)
    
    # Add export options for reports
    report_tab = st.expander("Generate Reports", expanded=False)
    with report_tab:
        st.markdown("### Export Reports")
        
        report_type = st.selectbox(
            "Select Report Type",
            ["Sales Summary", "Product Performance", "Category Analysis", "Time Series Analysis"],
            key="report_type"
        )
        
        # Create a buffer for the report
        report_buffer = io.BytesIO()
        
        # Generate different reports based on selection
        if report_type == "Sales Summary":
            with pd.ExcelWriter(report_buffer, engine='xlsxwriter') as writer:
                # Summary sheet
                summary_data = pd.DataFrame({
                    'Metric': ['Total Sales', 'Total Items Sold', 'Average Sale Value', 'Number of Transactions'],
                    'Value': [
                        f"₹{sales_data['Total'].sum():.2f}",
                        f"{sales_data['Quantity'].sum()}",
                        f"₹{sales_data['Total'].mean():.2f}",
                        f"{sales_data['Bill Number'].nunique()}"
                    ]
                })
                summary_data.to_excel(writer, sheet_name='Summary', index=False)
                
                # Daily sales
                daily_sales = sales_data.groupby(sales_data['Date'].dt.date)['Total'].sum().reset_index()
                daily_sales.to_excel(writer, sheet_name='Daily Sales', index=False)
                
                # Category sales
                if 'Category' in sales_data.columns:
                    category_sales = sales_data.groupby('Category')['Total'].sum().reset_index()
                    category_sales.to_excel(writer, sheet_name='Category Sales', index=False)
        
        elif report_type == "Product Performance":
            with pd.ExcelWriter(report_buffer, engine='xlsxwriter') as writer:
                if 'Product' in sales_data.columns:
                    # Product sales
                    product_sales = sales_data.groupby('Product')['Total'].sum().reset_index()
                    product_sales = product_sales.sort_values('Total', ascending=False)
                    product_sales.to_excel(writer, sheet_name='Product Sales', index=False)
                    
                    # Product quantities
                    product_qty = sales_data.groupby('Product')['Quantity'].sum().reset_index()
                    product_qty = product_qty.sort_values('Quantity', ascending=False)
                    product_qty.to_excel(writer, sheet_name='Product Quantities', index=False)
                    
                    # Combined product metrics
                    product_metrics = sales_data.groupby('Product').agg({
                        'Total': 'sum',
                        'Quantity': 'sum',
                        'Bill Number': 'nunique'
                    }).reset_index()
                    product_metrics.columns = ['Product', 'Total Sales', 'Quantity Sold', 'Number of Transactions']
                    product_metrics['Average Price'] = product_metrics['Total Sales'] / product_metrics['Quantity Sold']
                    product_metrics = product_metrics.sort_values('Total Sales', ascending=False)
                    product_metrics.to_excel(writer, sheet_name='Product Metrics', index=False)
        
        elif report_type == "Category Analysis":
            with pd.ExcelWriter(report_buffer, engine='xlsxwriter') as writer:
                if 'Category' in sales_data.columns:
                    # Category sales
                    category_sales = sales_data.groupby('Category')['Total'].sum().reset_index()
                    category_sales = category_sales.sort_values('Total', ascending=False)
                    category_sales.to_excel(writer, sheet_name='Category Sales', index=False)
                    
                    # Category quantities
                    category_qty = sales_data.groupby('Category')['Quantity'].sum().reset_index()
                    category_qty = category_qty.sort_values('Quantity', ascending=False)
                    category_qty.to_excel(writer, sheet_name='Category Quantities', index=False)
                    
                    # Products by category
                    if 'Product' in sales_data.columns:
                        category_products = sales_data.groupby(['Category', 'Product'])['Total'].sum().reset_index()
                        category_products = category_products.sort_values(['Category', 'Total'], ascending=[True, False])
                        category_products.to_excel(writer, sheet_name='Products by Category', index=False)
        
        elif report_type == "Time Series Analysis":
            with pd.ExcelWriter(report_buffer, engine='xlsxwriter') as writer:
                # Daily sales
                daily_sales = sales_data.groupby(sales_data['Date'].dt.date)['Total'].sum().reset_index()
                daily_sales.to_excel(writer, sheet_name='Daily Sales', index=False)
                
                # Weekly sales
                weekly_sales = sales_data.groupby(['Year', 'Week'])['Total'].sum().reset_index()
                weekly_sales['Period'] = weekly_sales['Year'].astype(str) + '-W' + weekly_sales['Week'].astype(str)
                weekly_sales.to_excel(writer, sheet_name='Weekly Sales', index=False)
                
                # Monthly sales
                monthly_sales = sales_data.groupby(['Year', 'MonthName'])['Total'].sum().reset_index()
                monthly_sales.to_excel(writer, sheet_name='Monthly Sales', index=False)
        
        # Download button for the report
        st.download_button(
            label=f"Download {report_type} Report",
            data=report_buffer.getvalue(),
            file_name=f"{report_type.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.ms-excel"
        )
    
    # Add a footer with timestamp
    st.markdown("---")
    st.markdown(f"<div style='text-align: center; color: gray; font-size: 0.8em;'>Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>", unsafe_allow_html=True)