import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import sys

# Add src to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_api import DataAPI
from data_collectors import DataCollector

# Page configuration
st.set_page_config(
    page_title="SME Decision Support Dashboard",
    page_icon="📊",
    layout="wide"
)

# Initialize data API
@st.cache_resource
def init_data_api():
    return DataAPI()

@st.cache_resource
def init_data_collector():
    return DataCollector()

# Title and description
st.title("🚀 AI-Powered Decision Support Dashboard")
st.markdown("**Phase 2**: Real Data Integration & APIs")

# Sidebar for controls
st.sidebar.header("📋 Dashboard Controls")

# Data refresh button
if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.cache_resource.clear()
    st.rerun()

# Data collection button
if st.sidebar.button("📥 Collect New Data"):
    with st.spinner("Collecting fresh data..."):
        collector = init_data_collector()
        collector.collect_all_data()
    st.success("✅ Data collection completed!")
    st.cache_data.clear()
    st.rerun()

# Initialize API
try:
    api = init_data_api()
    
    # Date range selector
    default_start = datetime.now() - timedelta(days=30)
    default_end = datetime.now()
    
    date_range = st.sidebar.date_input(
        "📅 Select Date Range",
        value=(default_start.date(), default_end.date()),
        max_value=datetime.now().date()
    )
    
    start_date, end_date = date_range if len(date_range) == 2 else (default_start.date(), default_end.date())
    
    # Load data
    with st.spinner("Loading data..."):
        sales_df = api.get_sales_data(start_date, end_date)
        stock_df = api.get_stock_data(start_date=start_date, end_date=end_date)
        news_df = api.get_news_data(start_date, end_date)
        feedback_df = api.get_customer_feedback(start_date, end_date)
        summary_metrics = api.get_summary_metrics()
    
    # Check if we have data
    if sales_df.empty:
        st.warning("⚠️ No data found. Please collect data first using the 'Collect New Data' button.")
        st.stop()
    
    # Filters in sidebar
    if not sales_df.empty:
        products = st.sidebar.multiselect(
            "📦 Select Products",
            options=sales_df['product'].unique(),
            default=sales_df['product'].unique()
        )
        
        regions = st.sidebar.multiselect(
            "🌍 Select Regions",
            options=sales_df['region'].unique(),
            default=sales_df['region'].unique()
        )
        
        # Filter sales data
        sales_filtered = sales_df[
            (sales_df['product'].isin(products)) &
            (sales_df['region'].isin(regions))
        ]
    else:
        sales_filtered = sales_df
    
    # Main dashboard content
    
    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_sales = sales_filtered['sales'].sum()
        st.metric("💰 Total Sales", f"${total_sales:,.0f}")
    
    with col2:
        avg_satisfaction = sales_filtered['customer_satisfaction'].mean()
        st.metric("😊 Avg Satisfaction", f"{avg_satisfaction:.1f}/5")
    
    with col3:
        avg_rating = feedback_df['rating'].mean() if not feedback_df.empty else 0
        st.metric("⭐ Avg Rating", f"{avg_rating:.1f}/5")
    
    with col4:
        news_sentiment = summary_metrics.get('news_sentiment', 0)
        sentiment_emoji = "😊" if news_sentiment > 0 else "😐" if news_sentiment == 0 else "😟"
        st.metric(f"{sentiment_emoji} News Sentiment", f"{news_sentiment:.2f}")
    
    # Stock prices row (if available)
    if not stock_df.empty and 'stock_prices' in summary_metrics:
        st.subheader("📈 Market Data")
        stock_cols = st.columns(len(summary_metrics['stock_prices']))
        
        for i, (symbol, price) in enumerate(summary_metrics['stock_prices'].items()):
            with stock_cols[i]:
                # Calculate price change if possible
                symbol_data = stock_df[stock_df['symbol'] == symbol].sort_values('date')
                if len(symbol_data) > 1:
                    prev_price = symbol_data.iloc[-2]['close']
                    change = price - prev_price
                    change_pct = (change / prev_price) * 100
                    st.metric(
                        f"📊 {symbol}",
                        f"${price:.2f}",
                        f"{change:+.2f} ({change_pct:+.1f}%)"
                    )
                else:
                    st.metric(f"📊 {symbol}", f"${price:.2f}")
    
    # Charts section
    st.subheader("📊 Business Analytics")
    
    # First row of charts
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.subheader("📈 Sales Trends")
        if not sales_filtered.empty:
            daily_sales = sales_filtered.groupby('date')['sales'].sum().reset_index()
            daily_sales['date'] = pd.to_datetime(daily_sales['date'])
            daily_sales = daily_sales.sort_values('date')
            
            fig_trend = px.line(
                daily_sales,
                x='date',
                y='sales',
                title="Daily Sales Performance",
                markers=True
            )
            fig_trend.update_layout(height=400)
            st.plotly_chart(fig_trend, use_container_width=True)
        else:
            st.info("No sales data for selected filters")
    
    with chart_col2:
        st.subheader("🥧 Product Distribution")
        if not sales_filtered.empty:
            product_sales = sales_filtered.groupby('product')['sales'].sum().reset_index()
            
            fig_pie = px.pie(
                product_sales,
                values='sales',
                names='product',
                title="Sales by Product"
            )
            fig_pie.update_layout(height=400)
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No sales data for selected filters")
    
    # Second row of charts
    chart_col3, chart_col4 = st.columns(2)
    
    with chart_col3:
        st.subheader("🌍 Regional Performance")
        if not sales_filtered.empty:
            regional_data = api.get_regional_performance()
            if not regional_data.empty:
                fig_region = px.bar(
                    regional_data,
                    x='region',
                    y='total_sales',
                    color='performance_score',
                    title="Sales by Region",
                    color_continuous_scale='viridis'
                )
                fig_region.update_layout(height=400)
                st.plotly_chart(fig_region, use_container_width=True)
            else:
                st.info("No regional data available")
        else:
            st.info("No sales data for selected filters")
    
    with chart_col4:
        st.subheader("💭 Sentiment Analysis")
        if not feedback_df.empty:
            # Create sentiment distribution
            sentiment_ranges = []
            sentiment_counts = []
            
            positive = len(feedback_df[feedback_df['sentiment_score'] > 0.1])
            neutral = len(feedback_df[(feedback_df['sentiment_score'] >= -0.1) & 
                                     (feedback_df['sentiment_score'] <= 0.1)])
            negative = len(feedback_df[feedback_df['sentiment_score'] < -0.1])
            
            sentiment_data = pd.DataFrame({
                'sentiment': ['Positive', 'Neutral', 'Negative'],
                'count': [positive, neutral, negative],
                'color': ['#2E8B57', '#FFD700', '#DC143C']
            })
            
            fig_sentiment = px.bar(
                sentiment_data,
                x='sentiment',
                y='count',
                color='sentiment',
                title="Customer Sentiment Distribution",
                color_discrete_map={'Positive': '#2E8B57', 'Neutral': '#FFD700', 'Negative': '#DC143C'}
            )
            fig_sentiment.update_layout(height=400)
            st.plotly_chart(fig_sentiment, use_container_width=True)
        else:
            st.info("No feedback data available")
    
    # Stock chart (if data available)
    if not stock_df.empty:
        st.subheader("📈 Stock Market Trends")
        
        # Stock symbol selector
        selected_symbol = st.selectbox(
            "Select Stock Symbol",
            options=stock_df['symbol'].unique(),
            index=0
        )
        
        symbol_data = stock_df[stock_df['symbol'] == selected_symbol].sort_values('date')
        
        if not symbol_data.empty:
            fig_stock = go.Figure()
            
            fig_stock.add_trace(go.Candlestick(
                x=symbol_data['date'],
                open=symbol_data['open'],
                high=symbol_data['high'],
                low=symbol_data['low'],
                close=symbol_data['close'],
                name=selected_symbol
            ))
            
            fig_stock.update_layout(
                title=f"{selected_symbol} Stock Price Movement",
                yaxis_title="Price ($)",
                xaxis_title="Date",
                height=400
            )
            
            st.plotly_chart(fig_stock, use_container_width=True)
    
    # News section
    if not news_df.empty:
        st.subheader("📰 Latest Business News")
        
        # Show top 5 news articles
        top_news = news_df.head(5)
        
        for index, article in top_news.iterrows():
            with st.expander(f"📄 {article['title'][:100]}..."):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**Source:** {article['source']}")
                    if article['description']:
                        st.write(article['description'])
                    st.write(f"**Published:** {article['published_at'].strftime('%Y-%m-%d %H:%M')}")
                
                with col2:
                    if article['sentiment_score'] is not None:
                        sentiment_color = 'green' if article['sentiment_score'] > 0 else 'red' if article['sentiment_score'] < 0 else 'gray'
                        st.markdown(f"**Sentiment:** <span style='color: {sentiment_color}'>{article['sentiment_score']:.2f}</span>", 
                                  unsafe_allow_html=True)
    
    # Data tables section
    with st.expander("📋 Raw Data Tables"):
        tab1, tab2, tab3, tab4 = st.tabs(["Sales Data", "Stock Data", "News Data", "Feedback"])
        
        with tab1:
            st.dataframe(sales_filtered, use_container_width=True)
        
        with tab2:
            if not stock_df.empty:
                st.dataframe(stock_df, use_container_width=True)
            else:
                st.info("No stock data available")
        
        with tab3:
            if not news_df.empty:
                st.dataframe(news_df[['title', 'source', 'published_at', 'sentiment_score']], 
                           use_container_width=True)
            else:
                st.info("No news data available")
        
        with tab4:
            if not feedback_df.empty:
                st.dataframe(feedback_df, use_container_width=True)
            else:
                st.info("No feedback data available")
    
    # Insights section
    st.subheader("💡 AI-Powered Insights")
    
    insights_col1, insights_col2 = st.columns(2)
    
    with insights_col1:
        st.markdown("### 📊 Performance Insights")
        
        if not sales_filtered.empty:
            # Best performing product
            product_performance = sales_filtered.groupby('product')['sales'].sum().sort_values(ascending=False)
            best_product = product_performance.index[0]
            best_sales = product_performance.iloc[0]
            st.success(f"🏆 Top Product: **{best_product}** (${best_sales:,.0f})")
            
            # Best region
            if not regions or len(regions) > 1:
                regional_performance = sales_filtered.groupby('region')['sales'].sum().sort_values(ascending=False)
                best_region = regional_performance.index[0]
                st.info(f"🌟 Top Region: **{best_region}**")
            
            # Satisfaction insight
            if sales_filtered['customer_satisfaction'].mean() > 4.0:
                st.success("😊 High customer satisfaction maintained!")
            elif sales_filtered['customer_satisfaction'].mean() < 3.5:
                st.warning("⚠️ Customer satisfaction needs attention")
    
    with insights_col2:
        st.markdown("### 🔮 Predictive Insights")
        
        if not sales_filtered.empty and len(sales_filtered) > 5:
            # Simple trend analysis
            recent_sales = sales_filtered.nlargest(7, 'date')['sales'].mean()
            older_sales = sales_filtered.nsmallest(7, 'date')['sales'].mean()
            
            if recent_sales > older_sales * 1.1:
                st.success("📈 Sales trending upward!")
            elif recent_sales < older_sales * 0.9:
                st.warning("📉 Sales showing decline trend")
            else:
                st.info("📊 Sales remain stable")
        
        # Market sentiment insight
        if news_sentiment > 0.2:
            st.success("📰 Positive market sentiment detected")
        elif news_sentiment < -0.2:
            st.warning("📰 Negative market sentiment - monitor closely")
        else:
            st.info("📰 Neutral market sentiment")

except Exception as e:
    st.error(f"❌ Error loading dashboard: {str(e)}")
    st.info("💡 Try collecting data first using the 'Collect New Data' button in the sidebar.")
    
    # Show error details in expander for debugging
    with st.expander("🔧 Debug Information"):
        st.code(str(e))
        import traceback
        st.code(traceback.format_exc())

# Footer
st.markdown("---")
st.markdown("**Phase 2 Complete** ✅ | Next: Advanced AI Integration")

# Status information
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Data Status")
if 'summary_metrics' in locals():
    if summary_metrics.get('data_freshness'):
        st.sidebar.success(f"✅ Data fresh as of: {summary_metrics['data_freshness'].strftime('%H:%M:%S')}")
st.sidebar.markdown("### 🔧 System Info")
st.sidebar.info("Phase 2: Real data integration active")