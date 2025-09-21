"""
Configuration file for Coffee Cupping App
"""
import os

# Database configuration
DATA_FILE = "coffee_app_data.json"
DATABASE_URL = os.getenv("DATABASE_URL", "coffee_cupping.db")

# App configuration
APP_NAME = "Coffee Cupping Professional"
APP_ICON = "☕"
COPYRIGHT = "© 2025 Rodrigo Bermudez - Cafe Cultura LLC"

# Demo credentials
DEMO_CREDENTIALS = {
    "email": "demo@coffee.com",
    "password": "demo123"
}

# SCA Scoring categories
SCA_CATEGORIES = [
    'fragrance', 'flavor', 'aftertaste', 'acidity', 
    'body', 'balance', 'uniformity', 'clean_cup', 
    'sweetness', 'overall'
]

# Flavor wheel categories
FLAVOR_CATEGORIES = {
    'Fruity': {
        'color': '#FF6B6B',
        'subcategories': {
            'Citrus': ['Grapefruit', 'Orange', 'Lemon', 'Lime'],
            'Berry': ['Blackberry', 'Raspberry', 'Blueberry', 'Strawberry'],
            'Stone Fruit': ['Peach', 'Apricot', 'Plum', 'Cherry'],
            'Tropical': ['Pineapple', 'Mango', 'Papaya', 'Coconut']
        }
    },
    'Sweet': {
        'color': '#FFD93D',
        'subcategories': {
            'Brown Sugar': ['Molasses', 'Maple Syrup', 'Caramelized', 'Honey'],
            'Vanilla': ['Vanilla Extract', 'Vanilla Bean'],
            'Chocolate': ['Dark Chocolate', 'Milk Chocolate', 'Cocoa']
        }
    },
    'Nutty': {
        'color': '#A0522D',
        'subcategories': {
            'Tree Nuts': ['Almond', 'Hazelnut', 'Walnut'],
            'Legumes': ['Peanut', 'Fresh Peanuts']
        }
    },
    'Spices': {
        'color': '#FF8C00',
        'subcategories': {
            'Pungent': ['Pepper', 'Clove', 'Anise'],
            'Warming': ['Cinnamon', 'Nutmeg', 'Cardamom']
        }
    },
    'Floral': {
        'color': '#DA70D6',
        'subcategories': {
            'Black Tea': ['Black Tea'],
            'Floral': ['Chamomile', 'Rose', 'Jasmine']
        }
    },
    'Other': {
        'color': '#708090',
        'subcategories': {
            'Cereal': ['Grain', 'Malt'],
            'Roasted': ['Pipe Tobacco', 'Burnt', 'Ashy']
        }
    }
}

# URL patterns for sharing
SHARE_URL_BASE = "https://coffee-cupping-app-final.streamlit.app"