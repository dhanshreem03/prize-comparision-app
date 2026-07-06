"""Database models for the prize comparison app."""
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()


class Product(db.Model):
    """Model to store product information from different sources."""

    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(255), nullable=False, index=True)
    source = db.Column(db.String(50), nullable=False)  # Amazon, Flipkart, etc.
    price = db.Column(db.String(50))  # Original price
    discounted_price = db.Column(db.String(50))  # Selling price
    image_url = db.Column(db.Text)
    product_url = db.Column(db.Text)
    screenshot_path = db.Column(db.String(255))
    # What user searched for
    search_query = db.Column(db.String(255), index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'product_name': self.product_name,
            'source': self.source,
            'price': self.price,
            'discounted_price': self.discounted_price,
            'image_url': self.image_url,
            'product_url': self.product_url,
            'search_query': self.search_query,
            'created_at': self.created_at.isoformat()
        }


class User(UserMixin, db.Model):
    """Model for user accounts with authentication."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True,
                         nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    search_histories = db.relationship(
        'SearchHistory', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        """Hash and set password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if provided password matches hash."""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_admin': self.is_admin,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }

    def __repr__(self):
        return f'<User {self.username}>'


class SearchHistory(db.Model):
    """Model to track user search history with results."""

    __tablename__ = 'search_history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id'), nullable=False, index=True)
    search_query = db.Column(db.String(255), nullable=False, index=True)
    results_count = db.Column(db.Integer, default=0)
    results_data = db.Column(db.Text)  # JSON string of results
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username,
            'search_query': self.search_query,
            'results_count': self.results_count,
            'created_at': self.created_at.isoformat()
        }

    def __repr__(self):
        return f'<SearchHistory {self.search_query} by {self.user.username}>'

    def __repr__(self):
        return f'<User {self.username}>'
