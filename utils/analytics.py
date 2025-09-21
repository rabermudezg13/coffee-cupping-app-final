"""
Analytics and data analysis module for Coffee Cupping App
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from typing import List, Dict, Any
from datetime import datetime, timedelta
import streamlit as st
from database.db_manager import db

class CuppingAnalytics:
    def __init__(self):
        self.categories = ['fragrance', 'flavor', 'aftertaste', 'acidity', 
                          'body', 'balance', 'uniformity', 'clean_cup', 
                          'sweetness', 'overall']
    
    def get_sessions_data(self) -> List[Dict]:
        """Get all cupping sessions data"""
        if db.db_type == 'json':
            data = db.load_json_data()
            return data.get('cupping_sessions', [])
        else:
            # SQLite implementation would go here
            return []
    
    def calculate_session_averages(self, session: Dict) -> Dict:
        """Calculate average scores for a session"""
        if 'scores' not in session or not session['scores']:
            return {}
        
        scores = session['scores']
        averages = {}
        
        for category in self.categories:
            values = [score.get(category, 0) for score in scores if score.get(category)]
            averages[category] = np.mean(values) if values else 0
        
        # Calculate overall average
        averages['total'] = np.mean([score.get('total', 0) for score in scores if score.get('total')])
        
        return averages
    
    def get_community_trends(self) -> Dict:
        """Analyze community trends and patterns"""
        sessions = self.get_sessions_data()
        if not sessions:
            return {}
        
        # Initialize trends data
        trends = {
            'total_sessions': len(sessions),
            'total_samples': 0,
            'average_scores': {},
            'popular_flavors': {},
            'score_distribution': [],
            'temporal_trends': [],
            'top_origins': {},
            'protocol_usage': {}
        }
        
        all_scores = []
        all_flavors = []
        monthly_data = {}
        origins = {}
        protocols = {}
        
        for session in sessions:
            if session.get('status') == 'Scored' and 'scores' in session:
                # Count samples
                trends['total_samples'] += len(session.get('samples', []))
                
                # Collect scores
                for score in session['scores']:
                    if score.get('total'):
                        all_scores.append(score['total'])
                        
                        # Collect flavors
                        if score.get('selected_flavors'):
                            all_flavors.extend(score['selected_flavors'])
                
                # Temporal analysis
                try:
                    session_date = datetime.fromisoformat(session['date'])
                    month_key = session_date.strftime('%Y-%m')
                    if month_key not in monthly_data:
                        monthly_data[month_key] = []
                    
                    session_avg = self.calculate_session_averages(session)
                    if session_avg.get('total'):
                        monthly_data[month_key].append(session_avg['total'])
                except:
                    pass
                
                # Origins analysis
                for sample in session.get('samples', []):
                    origin = sample.get('origin', 'Unknown')
                    origins[origin] = origins.get(origin, 0) + 1
                
                # Protocol analysis
                protocol = session.get('protocol', 'Unknown')
                protocols[protocol] = protocols.get(protocol, 0) + 1
        
        # Calculate averages
        if all_scores:
            trends['score_distribution'] = all_scores
            
            # Calculate category averages across all sessions
            for category in self.categories:
                category_scores = []
                for session in sessions:
                    if session.get('status') == 'Scored' and 'scores' in session:
                        for score in session['scores']:
                            if score.get(category):
                                category_scores.append(score[category])
                
                trends['average_scores'][category] = np.mean(category_scores) if category_scores else 0
        
        # Popular flavors
        if all_flavors:
            from collections import Counter
            flavor_counts = Counter(all_flavors)
            trends['popular_flavors'] = dict(flavor_counts.most_common(10))
        
        # Temporal trends
        for month, scores in monthly_data.items():
            if scores:
                trends['temporal_trends'].append({
                    'month': month,
                    'average_score': np.mean(scores),
                    'sessions_count': len(scores)
                })
        
        # Sort temporal trends
        trends['temporal_trends'].sort(key=lambda x: x['month'])
        
        # Top origins and protocols
        trends['top_origins'] = dict(sorted(origins.items(), key=lambda x: x[1], reverse=True)[:10])
        trends['protocol_usage'] = protocols
        
        return trends
    
    def create_radar_chart(self, session_data: Dict, title: str = "Cupping Profile") -> go.Figure:
        """Create interactive radar chart for session scores"""
        if 'scores' not in session_data or not session_data['scores']:
            return go.Figure()
        
        averages = self.calculate_session_averages(session_data)
        
        categories_display = [cat.replace('_', ' ').title() for cat in self.categories]
        values = [averages.get(cat, 0) for cat in self.categories]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories_display,
            fill='toself',
            name=title,
            line=dict(color='#8B4513', width=2),
            fillcolor='rgba(139, 69, 19, 0.1)'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[6, 10],
                    tickfont=dict(size=10),
                    gridcolor='rgba(139, 69, 19, 0.2)'
                ),
                angularaxis=dict(
                    tickfont=dict(size=12, color='#8B4513')
                )
            ),
            showlegend=True,
            title=dict(
                text=title,
                x=0.5,
                font=dict(size=16, color='#8B4513')
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#8B4513')
        )
        
        return fig
    
    def create_score_distribution(self, trends_data: Dict) -> go.Figure:
        """Create score distribution histogram"""
        scores = trends_data.get('score_distribution', [])
        if not scores:
            return go.Figure()
        
        fig = go.Figure()
        
        fig.add_trace(go.Histogram(
            x=scores,
            nbinsx=20,
            marker=dict(
                color='#8B4513',
                opacity=0.7,
                line=dict(color='#654321', width=1)
            ),
            name='Score Distribution'
        ))
        
        # Add mean line
        mean_score = np.mean(scores)
        fig.add_vline(
            x=mean_score,
            line_dash="dash",
            line_color="#D4AF37",
            annotation_text=f"Average: {mean_score:.1f}",
            annotation_position="top"
        )
        
        fig.update_layout(
            title="Community Score Distribution",
            xaxis_title="SCA Score",
            yaxis_title="Frequency",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#8B4513')
        )
        
        return fig
    
    def create_temporal_trends(self, trends_data: Dict) -> go.Figure:
        """Create temporal trends chart"""
        temporal_data = trends_data.get('temporal_trends', [])
        if not temporal_data:
            return go.Figure()
        
        dates = [item['month'] for item in temporal_data]
        scores = [item['average_score'] for item in temporal_data]
        session_counts = [item['sessions_count'] for item in temporal_data]
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Average scores line
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=scores,
                mode='lines+markers',
                name='Average Score',
                line=dict(color='#8B4513', width=3),
                marker=dict(size=8)
            ),
            secondary_y=False,
        )
        
        # Session count bars
        fig.add_trace(
            go.Bar(
                x=dates,
                y=session_counts,
                name='Sessions Count',
                opacity=0.3,
                marker=dict(color='#D2B48C')
            ),
            secondary_y=True,
        )
        
        fig.update_xaxes(title_text="Month")
        fig.update_yaxes(title_text="Average Score", secondary_y=False)
        fig.update_yaxes(title_text="Number of Sessions", secondary_y=True)
        
        fig.update_layout(
            title="Scoring Trends Over Time",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#8B4513'),
            hovermode='x unified'
        )
        
        return fig
    
    def create_flavor_popularity_chart(self, trends_data: Dict) -> go.Figure:
        """Create popular flavors chart"""
        popular_flavors = trends_data.get('popular_flavors', {})
        if not popular_flavors:
            return go.Figure()
        
        flavors = list(popular_flavors.keys())
        counts = list(popular_flavors.values())
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=counts,
            y=flavors,
            orientation='h',
            marker=dict(
                color='#8B4513',
                opacity=0.7
            ),
            text=counts,
            textposition='auto'
        ))
        
        fig.update_layout(
            title="Most Popular Flavor Notes",
            xaxis_title="Frequency",
            yaxis_title="Flavor Notes",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#8B4513'),
            height=max(400, len(flavors) * 30)
        )
        
        return fig
    
    def create_category_comparison(self, trends_data: Dict) -> go.Figure:
        """Create category comparison chart"""
        averages = trends_data.get('average_scores', {})
        if not averages:
            return go.Figure()
        
        categories = [cat.replace('_', ' ').title() for cat in self.categories]
        values = [averages.get(cat, 0) for cat in self.categories]
        
        # Color coding based on score ranges
        colors = ['#28a745' if v >= 8.5 else '#ffc107' if v >= 7.5 else '#dc3545' for v in values]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=categories,
            y=values,
            marker=dict(color=colors, opacity=0.8),
            text=[f'{v:.1f}' for v in values],
            textposition='auto'
        ))
        
        fig.update_layout(
            title="Average Scores by Category",
            xaxis_title="Cupping Categories",
            yaxis_title="Average Score",
            yaxis=dict(range=[6, 10]),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#8B4513')
        )
        
        return fig
    
    def generate_session_insights(self, session_data: Dict) -> Dict:
        """Generate insights for a specific session"""
        if 'scores' not in session_data or not session_data['scores']:
            return {}
        
        insights = {}
        scores = session_data['scores']
        
        # Calculate statistics
        total_scores = [score.get('total', 0) for score in scores if score.get('total')]
        if total_scores:
            insights['highest_score'] = max(total_scores)
            insights['lowest_score'] = min(total_scores)
            insights['average_score'] = np.mean(total_scores)
            insights['score_range'] = max(total_scores) - min(total_scores)
        
        # Best performing categories
        category_averages = {}
        for category in self.categories:
            category_scores = [score.get(category, 0) for score in scores if score.get(category)]
            if category_scores:
                category_averages[category] = np.mean(category_scores)
        
        if category_averages:
            best_category = max(category_averages.items(), key=lambda x: x[1])
            worst_category = min(category_averages.items(), key=lambda x: x[1])
            insights['best_category'] = {'name': best_category[0], 'score': best_category[1]}
            insights['worst_category'] = {'name': worst_category[0], 'score': worst_category[1]}
        
        # Most common flavors
        all_flavors = []
        for score in scores:
            if score.get('selected_flavors'):
                all_flavors.extend(score['selected_flavors'])
        
        if all_flavors:
            from collections import Counter
            flavor_counts = Counter(all_flavors)
            insights['top_flavors'] = dict(flavor_counts.most_common(5))
        
        return insights

# Global analytics instance
analytics = CuppingAnalytics()