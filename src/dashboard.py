import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="SME Decision Support Dashboard",
    page_icon="📊",
    layout="wide"
)

# Title and description
st.title("🚀 AI-Powered Decision Support Dashboard")
st.markdown("**Phase 1**: Basic Data Visualization for SMEs")

# Load data function
@st.cache_data
def load_data():
    """Load sample sales data"""
    try:
        df = pd.read_csv('../data/sample_sales.csv')
        df['date'] = pd.to_datetime(df['date'])
        return df
    except FileNotFoundError:
        st.error("Sample data file not found. Please check the data folder.")
        return None

# Load the data
df = load_data()

if df is not None:
    # Sidebar for filters
    st.sidebar.header("📋 Dashboard Controls")
    
    # Date range filter
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(df['date'].min(), df['date'].max()),
        min_value=df['date'].min(),
        max_value=df['date'].max()
    )
    
    # Product filter
    products = st.sidebar.multiselect(
        "Select Products",
        options=df['product'].unique(),
        default=df['product'].unique()
    )
    
    # Region filter
    regions = st.sidebar.multiselect(
        "Select Regions",
        options=df['region'].unique(),
        default=df['region'].unique()
    )
    
    # Filter data based on selections
    mask = (
        (df['date'] >= pd.to_datetime(date_range[0])) & 
        (df['date'] <= pd.to_datetime(date_range[1])) &
        (df['product'].isin(products)) &
        (df['region'].isin(regions))
    )
    filtered_df = df[mask]
    
    # Main dashboard content
    col1, col2, col3, col4 = st.columns(4)
    
    # Key metrics
    with col1:
        total_sales = filtered_df['sales'].sum()
        st.metric("💰 Total Sales", f"${total_sales:,}")
    
    with col2:
        avg_satisfaction = filtered_df['customer_satisfaction'].mean()
        st.metric("😊 Avg Satisfaction", f"{avg_satisfaction:.1f}/5")
    
    with col3:
        total_products = len(filtered_df['product'].unique())
        st.metric("📦 Products", total_products)
    
    with col4:
        total_regions = len(filtered_df['region'].unique())
        st.metric("🌍 Regions", total_regions)
    
    # Charts row 1
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Sales Trends Over Time")
        # Line chart for sales trends
        sales_by_date = filtered_df.groupby('date')['sales'].sum().reset_index()
        fig_line = px.line(
            sales_by_date, 
            x='date', 
            y='sales',
            title="Daily Sales Trends",
            markers=True
        )
        fig_line.update_layout(height=400)
        st.plotly_chart(fig_line, use_container_width=True)
    
    with col2:
        st.subheader("🥧 Sales by Product")
        # Pie chart for product sales
        sales_by_product = filtered_df.groupby('product')['sales'].sum().reset_index()
        fig_pie = px.pie(
            sales_by_product,
            values='sales',
            names='product',
            title="Sales Distribution by Product"
        )
        fig_pie.update_layout(height=400)
        st.plotly_chart(fig_pie, use_container_width=True)
    
    # Charts row 2
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Sales by Region")
        # Bar chart for regional sales
        sales_by_region = filtered_df.groupby('region')['sales'].sum().reset_index()
        fig_bar = px.bar(
            sales_by_region,
            x='region',
            y='sales',
            title="Regional Sales Performance",
            color='sales',
            color_continuous_scale='viridis'
        )
        fig_bar.update_layout(height=400)
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with col2:
        st.subheader("⭐ Satisfaction vs Sales")
        # Scatter plot
        fig_scatter = px.scatter(
            filtered_df,
            x='customer_satisfaction',
            y='sales',
            color='product',
            size='sales',
            title="Customer Satisfaction vs Sales Performance"
        )
        fig_scatter.update_layout(height=400)
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Data table
    st.subheader("📋 Raw Data Preview")
    with st.expander("View Detailed Data"):
        st.dataframe(filtered_df, use_container_width=True)
    
    # Summary insights
    st.subheader("💡 Key Insights")
    insights_col1, insights_col2 = st.columns(2)
    
    with insights_col1:
        best_product = sales_by_product.loc[sales_by_product['sales'].idxmax(), 'product']
        st.success(f"🏆 Best performing product: **{best_product}**")
        
        best_region = sales_by_region.loc[sales_by_region['sales'].idxmax(), 'region']
        st.info(f"🌟 Top region: **{best_region}**")
    
    with insights_col2:
        highest_satisfaction = filtered_df.loc[filtered_df['customer_satisfaction'].idxmax()]
        st.success(f"😊 Highest satisfaction: **{highest_satisfaction['customer_satisfaction']}/5** ({highest_satisfaction['product']})")
        
        total_revenue = filtered_df['sales'].sum()
        st.metric("📊 Total Revenue", f"${total_revenue:,}")

else:
    st.error("Unable to load data. Please check your data file.")

# Footer
st.markdown("---")
st.markdown("**Phase 1 Complete** ✅ | Next: Data Integration & APIs")