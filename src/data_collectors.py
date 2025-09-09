import requests
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import random
import json
from models import SessionLocal, SalesData, StockData, NewsData, CustomerFeedback

# Load environment variables
load_dotenv()

class DataCollector:
    def __init__(self):
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        self.news_api_key = os.getenv('NEWS_API_KEY')
        self.db = SessionLocal()
    
    def collect_stock_data(self, symbols=['AAPL', 'GOOGL', 'MSFT'], days=30):
        """Collect stock data using yfinance (free alternative to Alpha Vantage)"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            for symbol in symbols:
                print(f"Collecting data for {symbol}...")
                
                # Get stock data
                stock = yf.Ticker(symbol)
                hist = stock.history(start=start_date, end=end_date)
                
                # Save to database
                for date, row in hist.iterrows():
                    stock_record = StockData(
                        symbol=symbol,
                        date=date,
                        open_price=float(row['Open']),
                        high_price=float(row['High']),
                        low_price=float(row['Low']),
                        close_price=float(row['Close']),
                        volume=int(row['Volume'])
                    )
                    
                    # Check if record already exists
                    existing = self.db.query(StockData).filter(
                        StockData.symbol == symbol,
                        StockData.date == date
                    ).first()
                    
                    if not existing:
                        self.db.add(stock_record)
                
                self.db.commit()
                print(f"✅ Collected {symbol} data")
                
        except Exception as e:
            print(f"❌ Error collecting stock data: {e}")
            self.db.rollback()
    
    def collect_news_data(self, query='business technology', days=7):
        """Collect news data for sentiment analysis"""
        if not self.news_api_key or self.news_api_key == 'your_key_here':
            print("⚠️ No NewsAPI key found. Generating sample news data...")
            self.generate_sample_news()
            return
        
        try:
            url = 'https://newsapi.org/v2/everything'
            
            # Calculate date range
            to_date = datetime.now()
            from_date = to_date - timedelta(days=days)
            
            params = {
                'q': query,
                'from': from_date.strftime('%Y-%m-%d'),
                'to': to_date.strftime('%Y-%m-%d'),
                'sortBy': 'publishedAt',
                'apiKey': self.news_api_key,
                'language': 'en',
                'pageSize': 50
            }
            
            response = requests.get(url, params=params)
            data = response.json()
            
            if data['status'] == 'ok':
                for article in data['articles']:
                    news_record = NewsData(
                        title=article['title'][:500],  # Truncate if too long
                        description=article['description'][:1000] if article['description'] else None,
                        source=article['source']['name'],
                        published_at=datetime.fromisoformat(article['publishedAt'].replace('Z', '+00:00')),
                        url=article['url']
                    )
                    
                    # Check if record already exists
                    existing = self.db.query(NewsData).filter(
                        NewsData.title == news_record.title
                    ).first()
                    
                    if not existing:
                        self.db.add(news_record)
                
                self.db.commit()
                print(f"✅ Collected {len(data['articles'])} news articles")
            else:
                print(f"❌ News API error: {data.get('message', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Error collecting news data: {e}")
            self.db.rollback()
    
    def generate_sample_news(self):
        """Generate sample news data when API key is not available"""
        sample_news = [
            {
                'title': 'Tech Companies Report Strong Q4 Earnings',
                'description': 'Major technology companies exceeded expectations in quarterly earnings reports.',
                'source': 'Tech News Daily',
                'sentiment': 0.8
            },
            {
                'title': 'Market Volatility Continues Amid Economic Uncertainty',
                'description': 'Financial markets show continued volatility as investors react to economic indicators.',
                'source': 'Financial Times',
                'sentiment': -0.3
            },
            {
                'title': 'Small Businesses Embrace Digital Transformation',
                'description': 'SMEs increasingly adopt digital tools to improve efficiency and customer service.',
                'source': 'Business Weekly',
                'sentiment': 0.6
            },
            {
                'title': 'Consumer Confidence Reaches New Highs',
                'description': 'Latest survey shows consumer confidence at highest level in two years.',
                'source': 'Economic Review',
                'sentiment': 0.7
            },
            {
                'title': 'Supply Chain Disruptions Impact Global Trade',
                'description': 'Ongoing supply chain issues continue to affect international commerce.',
                'source': 'Global Trade Monitor',
                'sentiment': -0.4
            }
        ]
        
        for news_item in sample_news:
            # Generate random date within last week
            days_ago = random.randint(1, 7)
            pub_date = datetime.now() - timedelta(days=days_ago)
            
            news_record = NewsData(
                title=news_item['title'],
                description=news_item['description'],
                source=news_item['source'],
                published_at=pub_date,
                sentiment_score=news_item['sentiment'],
                url=f"https://example.com/news/{random.randint(1000, 9999)}"
            )
            
            # Check if record already exists
            existing = self.db.query(NewsData).filter(
                NewsData.title == news_record.title
            ).first()
            
            if not existing:
                self.db.add(news_record)
        
        self.db.commit()
        print("✅ Generated sample news data")
    
    def generate_enhanced_sales_data(self, days=30):
        """Generate more realistic sales data"""
        products = ['Product A', 'Product B', 'Product C', 'Product D']
        regions = ['North', 'South', 'East', 'West', 'Central']
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Generate data for each day
        current_date = start_date
        while current_date <= end_date:
            for product in products:
                for region in regions:
                    # Skip some combinations randomly to make data more realistic
                    if random.random() < 0.3:
                        continue
                    
                    # Generate realistic sales figures
                    base_sales = random.randint(800, 2500)
                    
                    # Add seasonal trends
                    day_of_year = current_date.timetuple().tm_yday
                    seasonal_factor = 1 + 0.3 * abs(math.sin(2 * math.pi * day_of_year / 365))
                    
                    sales = int(base_sales * seasonal_factor)
                    satisfaction = round(random.uniform(3.0, 5.0), 1)
                    
                    sales_record = SalesData(
                        date=current_date,
                        product=product,
                        sales=sales,
                        region=region,
                        customer_satisfaction=satisfaction
                    )
                    
                    # Check if record already exists
                    existing = self.db.query(SalesData).filter(
                        SalesData.date == current_date,
                        SalesData.product == product,
                        SalesData.region == region
                    ).first()
                    
                    if not existing:
                        self.db.add(sales_record)
            
            current_date += timedelta(days=1)
        
        self.db.commit()
        print(f"✅ Generated enhanced sales data for {days} days")
    
    def generate_customer_feedback(self, count=50):
        """Generate sample customer feedback for sentiment analysis"""
        products = ['Product A', 'Product B', 'Product C', 'Product D']
        
        positive_feedback = [
            "Excellent product quality, very satisfied with purchase",
            "Great customer service and fast delivery",
            "Product exceeded my expectations, highly recommend",
            "Amazing value for money, will buy again",
            "Perfect solution for my needs, love it"
        ]
        
        negative_feedback = [
            "Product quality was disappointing",
            "Delivery took too long, poor customer service",
            "Not worth the price, expected better",
            "Product arrived damaged, unsatisfied",
            "Difficult to use, poor user experience"
        ]
        
        neutral_feedback = [
            "Product is okay, meets basic requirements",
            "Average quality, nothing special",
            "Decent product but room for improvement",
            "Standard product, got what I expected",
            "Fair price for what you get"
        ]
        
        for i in range(count):
            # Choose feedback type randomly
            feedback_type = random.choices(
                ['positive', 'negative', 'neutral'],
                weights=[0.6, 0.2, 0.2]
            )[0]
            
            if feedback_type == 'positive':
                text = random.choice(positive_feedback)
                rating = random.uniform(4.0, 5.0)
                sentiment = random.uniform(0.5, 1.0)
            elif feedback_type == 'negative':
                text = random.choice(negative_feedback)
                rating = random.uniform(1.0, 2.5)
                sentiment = random.uniform(-1.0, -0.3)
            else:
                text = random.choice(neutral_feedback)
                rating = random.uniform(2.5, 4.0)
                sentiment = random.uniform(-0.2, 0.2)
            
            # Generate random date within last 30 days
            days_ago = random.randint(1, 30)
            feedback_date = datetime.now() - timedelta(days=days_ago)
            
            feedback_record = CustomerFeedback(
                customer_id=f"CUST{random.randint(1000, 9999)}",
                product=random.choice(products),
                feedback_text=text,
                rating=round(rating, 1),
                sentiment_score=round(sentiment, 2),
                date=feedback_date
            )
            
            self.db.add(feedback_record)
        
        self.db.commit()
        print(f"✅ Generated {count} customer feedback records")
    
    def collect_all_data(self):
        """Collect all types of data"""
        print("🚀 Starting data collection...")
        
        # Create tables if they don't exist
        from models import create_tables
        create_tables()
        
        # Collect all data types
        self.generate_enhanced_sales_data(30)
        self.collect_stock_data(['AAPL', 'GOOGL', 'MSFT'], 30)
        self.collect_news_data('business technology', 7)
        self.generate_customer_feedback(50)
        
        print("✅ Data collection completed!")
    
    def __del__(self):
        """Close database connection"""
        if hasattr(self, 'db'):
            self.db.close()

# Add math import at the top
import math

if __name__ == "__main__":
    collector = DataCollector()
    collector.collect_all_data()