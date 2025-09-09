from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

Base = declarative_base()

class SalesData(Base):
    __tablename__ = 'sales_data'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, nullable=False)
    product = Column(String(100), nullable=False)
    sales = Column(Float, nullable=False)
    region = Column(String(50), nullable=False)
    customer_satisfaction = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class StockData(Base):
    __tablename__ = 'stock_data'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(10), nullable=False)
    date = Column(DateTime, nullable=False)
    open_price = Column(Float, nullable=False)
    high_price = Column(Float, nullable=False)
    low_price = Column(Float, nullable=False)
    close_price = Column(Float, nullable=False)
    volume = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class NewsData(Base):
    __tablename__ = 'news_data'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    source = Column(String(100), nullable=False)
    published_at = Column(DateTime, nullable=False)
    sentiment_score = Column(Float, nullable=True)  # We'll calculate this later
    url = Column(String(1000), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class CustomerFeedback(Base):
    __tablename__ = 'customer_feedback'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(String(50), nullable=False)
    product = Column(String(100), nullable=False)
    feedback_text = Column(Text, nullable=False)
    rating = Column(Float, nullable=False)
    sentiment_score = Column(Float, nullable=True)  # We'll calculate this later
    date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# Database setup
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./data/business_data.db')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Create all tables in the database"""
    Base.metadata.create_all(bind=engine)
    
def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()