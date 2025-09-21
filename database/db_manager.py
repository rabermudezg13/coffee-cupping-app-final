"""
Database management for Coffee Cupping App
Supports both JSON and SQLite persistence
"""
import json
import sqlite3
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
import streamlit as st

class DatabaseManager:
    def __init__(self, db_type='json', db_path='coffee_app_data.json'):
        self.db_type = db_type
        self.db_path = db_path
        
        if db_type == 'sqlite':
            self.init_sqlite()
        else:
            self.init_json()
    
    def init_sqlite(self):
        """Initialize SQLite database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                preferences TEXT DEFAULT '{}'
            )
        ''')
        
        # Cupping sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cupping_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                share_id TEXT UNIQUE,
                user_email TEXT,
                name TEXT NOT NULL,
                date TEXT NOT NULL,
                cupper TEXT,
                protocol TEXT,
                water_temp INTEGER,
                cups_per_sample INTEGER,
                blind BOOLEAN,
                status TEXT,
                session_notes TEXT,
                anonymous_mode BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_email) REFERENCES users (email)
            )
        ''')
        
        # Samples table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS samples (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                name TEXT NOT NULL,
                origin TEXT,
                variety TEXT,
                process TEXT,
                altitude TEXT,
                harvest_year TEXT,
                FOREIGN KEY (session_id) REFERENCES cupping_sessions (session_id)
            )
        ''')
        
        # Scores table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                sample_name TEXT NOT NULL,
                fragrance REAL,
                flavor REAL,
                aftertaste REAL,
                acidity REAL,
                body REAL,
                balance REAL,
                uniformity REAL,
                clean_cup REAL,
                sweetness REAL,
                overall REAL,
                defects REAL,
                total REAL,
                notes TEXT,
                selected_flavors TEXT,
                FOREIGN KEY (session_id) REFERENCES cupping_sessions (session_id)
            )
        ''')
        
        # Coffee reviews table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS coffee_reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_email TEXT,
                coffee_name TEXT NOT NULL,
                rating INTEGER,
                origin TEXT,
                producer TEXT,
                cost REAL,
                roast_level TEXT,
                roast_date TEXT,
                grind_size TEXT,
                preparation_method TEXT,
                dry_aroma TEXT,
                wet_aroma TEXT,
                flavor_notes TEXT,
                recommendations TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_email) REFERENCES users (email)
            )
        ''')
        
        # Analytics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                session_id TEXT,
                user_email TEXT,
                data TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def init_json(self):
        """Initialize JSON data structure"""
        if not os.path.exists(self.db_path):
            initial_data = {
                'users': [],
                'cupping_sessions': [],
                'coffee_reviews': [],
                'analytics': []
            }
            self.save_json_data(initial_data)
    
    def load_json_data(self) -> Dict:
        """Load data from JSON file"""
        try:
            with open(self.db_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {'users': [], 'cupping_sessions': [], 'coffee_reviews': [], 'analytics': []}
    
    def save_json_data(self, data: Dict):
        """Save data to JSON file"""
        try:
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            st.error(f"Error saving data: {e}")
    
    def generate_share_id(self) -> str:
        """Generate unique share ID for cupping sessions"""
        return str(uuid.uuid4())[:8]
    
    def save_cupping_session(self, session_data: Dict, anonymous_mode: bool = False) -> str:
        """Save cupping session and return share ID"""
        share_id = self.generate_share_id()
        session_data['share_id'] = share_id
        session_data['anonymous_mode'] = anonymous_mode
        session_data['created_at'] = datetime.now().isoformat()
        session_data['updated_at'] = datetime.now().isoformat()
        
        if self.db_type == 'sqlite':
            return self._save_session_sqlite(session_data)
        else:
            return self._save_session_json(session_data)
    
    def _save_session_sqlite(self, session_data: Dict) -> str:
        """Save session to SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Insert session
            cursor.execute('''
                INSERT INTO cupping_sessions 
                (session_id, share_id, user_email, name, date, cupper, protocol, 
                 water_temp, cups_per_sample, blind, status, session_notes, anonymous_mode)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session_data.get('session_id', str(uuid.uuid4())),
                session_data['share_id'],
                session_data.get('user_email'),
                session_data['name'],
                session_data['date'],
                session_data.get('cupper'),
                session_data.get('protocol'),
                session_data.get('water_temp'),
                session_data.get('cups_per_sample'),
                session_data.get('blind'),
                session_data.get('status'),
                session_data.get('session_notes'),
                session_data['anonymous_mode']
            ))
            
            # Insert samples and scores if available
            session_id = session_data.get('session_id', str(uuid.uuid4()))
            
            if 'samples' in session_data:
                for sample in session_data['samples']:
                    cursor.execute('''
                        INSERT INTO samples (session_id, name, origin, variety, process, altitude, harvest_year)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        session_id, sample['name'], sample.get('origin'),
                        sample.get('variety'), sample.get('process'),
                        sample.get('altitude'), sample.get('harvest_year')
                    ))
            
            if 'scores' in session_data:
                for score in session_data['scores']:
                    cursor.execute('''
                        INSERT INTO scores 
                        (session_id, sample_name, fragrance, flavor, aftertaste, acidity,
                         body, balance, uniformity, clean_cup, sweetness, overall, defects,
                         total, notes, selected_flavors)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        session_id, score['sample_name'], score.get('fragrance'),
                        score.get('flavor'), score.get('aftertaste'), score.get('acidity'),
                        score.get('body'), score.get('balance'), score.get('uniformity'),
                        score.get('clean_cup'), score.get('sweetness'), score.get('overall'),
                        score.get('defects'), score.get('total'), score.get('notes'),
                        json.dumps(score.get('selected_flavors', []))
                    ))
            
            conn.commit()
            return session_data['share_id']
            
        except Exception as e:
            conn.rollback()
            st.error(f"Error saving session: {e}")
            return None
        finally:
            conn.close()
    
    def _save_session_json(self, session_data: Dict) -> str:
        """Save session to JSON file"""
        data = self.load_json_data()
        data['cupping_sessions'].append(session_data)
        self.save_json_data(data)
        return session_data['share_id']
    
    def get_session_by_share_id(self, share_id: str) -> Optional[Dict]:
        """Get cupping session by share ID"""
        if self.db_type == 'sqlite':
            return self._get_session_sqlite(share_id)
        else:
            return self._get_session_json(share_id)
    
    def _get_session_sqlite(self, share_id: str) -> Optional[Dict]:
        """Get session from SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get session data
            cursor.execute('SELECT * FROM cupping_sessions WHERE share_id = ?', (share_id,))
            session_row = cursor.fetchone()
            
            if not session_row:
                return None
            
            # Convert row to dict
            columns = [desc[0] for desc in cursor.description]
            session = dict(zip(columns, session_row))
            
            # Get samples
            cursor.execute('SELECT * FROM samples WHERE session_id = ?', (session['session_id'],))
            samples_rows = cursor.fetchall()
            sample_columns = [desc[0] for desc in cursor.description]
            session['samples'] = [dict(zip(sample_columns, row)) for row in samples_rows]
            
            # Get scores
            cursor.execute('SELECT * FROM scores WHERE session_id = ?', (session['session_id'],))
            scores_rows = cursor.fetchall()
            score_columns = [desc[0] for desc in cursor.description]
            scores = []
            for row in scores_rows:
                score = dict(zip(score_columns, row))
                if score['selected_flavors']:
                    score['selected_flavors'] = json.loads(score['selected_flavors'])
                scores.append(score)
            session['scores'] = scores
            
            return session
            
        except Exception as e:
            st.error(f"Error retrieving session: {e}")
            return None
        finally:
            conn.close()
    
    def _get_session_json(self, share_id: str) -> Optional[Dict]:
        """Get session from JSON file"""
        data = self.load_json_data()
        for session in data['cupping_sessions']:
            if session.get('share_id') == share_id:
                return session
        return None
    
    def log_analytics_event(self, event_type: str, session_id: str = None, 
                          user_email: str = None, data: Dict = None):
        """Log analytics event"""
        event = {
            'event_type': event_type,
            'session_id': session_id,
            'user_email': user_email,
            'data': json.dumps(data) if data else None,
            'timestamp': datetime.now().isoformat()
        }
        
        if self.db_type == 'sqlite':
            self._log_event_sqlite(event)
        else:
            self._log_event_json(event)
    
    def _log_event_sqlite(self, event: Dict):
        """Log event to SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO analytics (event_type, session_id, user_email, data)
                VALUES (?, ?, ?, ?)
            ''', (event['event_type'], event['session_id'], 
                  event['user_email'], event['data']))
            conn.commit()
        except Exception as e:
            st.error(f"Error logging event: {e}")
        finally:
            conn.close()
    
    def _log_event_json(self, event: Dict):
        """Log event to JSON"""
        data = self.load_json_data()
        if 'analytics' not in data:
            data['analytics'] = []
        data['analytics'].append(event)
        self.save_json_data(data)
    
    def get_analytics_data(self) -> List[Dict]:
        """Get analytics data for dashboard"""
        if self.db_type == 'sqlite':
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            try:
                cursor.execute('SELECT * FROM analytics ORDER BY timestamp DESC')
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                return [dict(zip(columns, row)) for row in rows]
            finally:
                conn.close()
        else:
            data = self.load_json_data()
            return data.get('analytics', [])

# Global database instance
db = DatabaseManager()