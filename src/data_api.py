import pandas as pd
from sqlalchemy.orm import sessionmaker
from models import engine, SalesData, StockData, NewsData, CustomerFeedback
from datetime import datetime, timedelta
import streamlit as st

class DataAPI:
    def __init__(self):
        SessionLocal = sessionmaker(bind=engine)
        self.db = SessionLocal()
    
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def get_sales_data(_self, start_date=None, end_date=None):
        """Get sales data from database"""
        query = _self.db.query(SalesData)
        
        if start_date:
            query = query.filter(SalesData.date >= start_date)
        if end_date:
            query = query.filter(SalesData.date <= end_date)
        
        results = query.all()
        
        # Convert to DataFrame
        data = []
        for record in results:
            data.append({
                'id': record.id,
                'date': record.date,
                'product': record.product,
                'sales': record.sales,
                'region': record.region,
                'customer_satisfaction': record.customer_satisfaction
            })
        
        return pd.DataFrame(data)
    
    @st.cache_data(ttl=300)
    def get_stock_data(_self, symbols=None, start_date=None, end_date=None):
        """Get stock data from database"""
        query = _self.db.query(StockData)
        
        if symbols:
            query = query.filter(StockData.symbol.in_(symbols))
        if start_date:
            query = query.filter(StockData.date >= start_date)
        if end_date:
            query = query.filter(StockData.date <= end_date)
        
        results = query.all()
        
        # Convert to DataFrame
        data = []
        for record in results:
            data.append({
                'symbol': record.symbol,
                'date': record.date,
                'open': record.open_price,
                'high': record.high_price,
                'low': record.low_price,
                'close': record.close_price,
                'volume': record.volume
            })
        
        return pd.DataFrame(data)
    
    @st.cache_data(ttl=600)  # Cache for 10 minutes
    def get_news_data(_self, start_date=None, end_date=None):
        """Get news data from database"""
        query = _self.db.query(NewsData)
        
        if start_date:
            query = query.filter(NewsData.published_at >= start_date)
        if end_date:
            query = query.filter(NewsData.published_at <= end_date)
        
        # Order by published date (newest first)
        query = query.order_by(NewsData.published_at.desc())
        
        results = query.all()
        
        # Convert to DataFrame
        data = []
        for record in results:
            data.append({
                'title': record.title,
                'description': record.description,
                'source': record.source,
                'published_at': record.published_at,
                'sentiment_score': record.sentiment_score,
                'url': record.url
            })
        
        return pd.DataFrame(data)
    
    @st.cache_data(ttl=300)
    def get_customer_feedback(_self, start_date=None, end_date=None):
        """Get customer feedback from database"""
        query = _self.db.query(CustomerFeedback)
        
        if start_date:
            query = query.filter(CustomerFeedback.date >= start_date)
        if end_date:
            query = query.filter(CustomerFeedback.date <= end_date)
        
        results = query.all()
        
        # Convert to DataFrame
        data = []
        for record in results:
            data.append({
                'customer_id': record.customer_id,
                'product': record.product,
                'feedback_text': record.feedback_text,
                'rating': record.rating,
                'sentiment_score': record.sentiment_score,
                'date': record.date
            })
        
        return pd.DataFrame(data)
    
    def get_summary_metrics(self):
        """Get key summary metrics"""
        try:
            # Sales metrics
            sales_df = self.get_sales_data()
            total_sales = sales_df['sales'].sum() if not sales_df.empty else 0
            avg_satisfaction = sales_df['customer_satisfaction'].mean() if not sales_df.empty else 0
            
            # Customer feedback metrics
            feedback_df = self.get_customer_feedback()
            avg_rating = feedback_df['rating'].mean() if not feedback_df.empty else 0
            avg_sentiment = feedback_df['sentiment_score'].mean() if not feedback_df.empty else 0
            
            # News sentiment
            news_df = self.get_news_data()
            news_sentiment = news_df['sentiment_score'].mean() if not news_df.empty else 0
            
            # Stock data
            stock_df = self.get_stock_data()
            latest_prices = {}
            if not stock_df.empty:
                for symbol in stock_df['symbol'].unique():
                    symbol_data = stock_df[stock_df['symbol'] == symbol].sort_values('date')
                    if not symbol_data.empty:
                        latest_prices[symbol] = symbol_data.iloc[-1]['close']
            
            return {
                'total_sales': total_sales,
                'avg_satisfaction': avg_satisfaction,
                'avg_rating': avg_rating,
                'avg_sentiment': avg_sentiment,
                'news_sentiment': news_sentiment,
                'stock_prices': latest_prices,
                'data_freshness': datetime.now()
            }
        except Exception as e:
            st.error(f"Error getting summary metrics: {e}")
            return {}
    
    def get_trending_products(self, days=7):
        """Get trending products based on recent sales"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        sales_df = self.get_sales_data(start_date, end_date)
        if sales_df.empty:
            return pd.DataFrame()
        
        trending = sales_df.groupby('product').agg({
            'sales': ['sum', 'mean', 'count'],
            'customer_satisfaction': 'mean'
        }).round(2)
        
        # Flatten column names
        trending.columns = ['total_sales', 'avg_sales', 'transaction_count', 'avg_satisfaction']
        trending = trending.reset_index()
        
        # Sort by total sales
        trending = trending.sort_values('total_sales', ascending=False)
        
        return trending
    
    def get_regional_performance(self, days=30):
        """Get regional performance metrics"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        sales_df = self.get_sales_data(start_date, end_date)
        if sales_df.empty:
            return pd.DataFrame()
        
        regional = sales_df.groupby('region').agg({
            'sales': ['sum', 'mean', 'count'],
            'customer_satisfaction': 'mean'
        }).round(2)
        
        # Flatten column names
        regional.columns = ['total_sales', 'avg_sales', 'transaction_count', 'avg_satisfaction']
        regional = regional.reset_index()
        
        # Calculate performance score (weighted average)
        regional['performance_score'] = (
            regional['avg_satisfaction'] * 0.4 + 
            (regional['avg_sales'] / regional['avg_sales'].max()) * 5 * 0.6
        ).round(2)
        
        return regional.sort_values('performance_score', ascending=False)
    
    def get_sentiment_analysis(self):
        """Get overall sentiment analysis from feedback and news"""
        feedback_df = self.get_customer_feedback()
        news_df = self.get_news_data()
        
        analysis = {
            'customer_sentiment': {
                'avg_score': feedback_df['sentiment_score'].mean() if not feedback_df.empty else 0,
                'positive_count': len(feedback_df[feedback_df['sentiment_score'] > 0.1]) if not feedback_df.empty else 0,
                'negative_count': len(feedback_df[feedback_df['sentiment_score'] < -0.1]) if not feedback_df.empty else 0,
                'neutral_count': len(feedback_df[(feedback_df['sentiment_score'] >= -0.1) & 
                                               (feedback_df['sentiment_score'] <= 0.1)]) if not feedback_df.empty else 0
            },
            'news_sentiment': {
                'avg_score': news_df['sentiment_score'].mean() if not news_df.empty else 0,
                'positive_count': len(news_df[news_df['sentiment_score'] > 0.1]) if not news_df.empty else 0,
                'negative_count': len(news_df[news_df['sentiment_score'] < -0.1]) if not news_df.empty else 0,
                'neutral_count': len(news_df[(news_df['sentiment_score'] >= -0.1) & 
                                           (news_df['sentiment_score'] <= 0.1)]) if not news_df.empty else 0
            }
        }
        
        return analysis
    
    def __del__(self):
        """Close database connection"""
        if hasattr(self, 'db'):
            self.db.close()