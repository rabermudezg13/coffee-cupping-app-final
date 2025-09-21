"""
Public cupping session display page
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from database.db_manager import db
from utils.analytics import analytics
from styles.themes import apply_custom_css, get_theme_colors, create_metric_card
from config import COPYRIGHT
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Wedge
import tempfile

def render_public_cupping_page(share_id: str):
    """Render public cupping session page"""
    # Apply styling
    apply_custom_css()
    colors = get_theme_colors()
    
    # Get session data
    session_data = db.get_session_by_share_id(share_id)
    
    if not session_data:
        st.error("🔍 Cupping session not found or may have been removed.")
        st.info("Please check the share link and try again.")
        return
    
    # Log page view
    db.log_analytics_event('public_view', session_id=share_id)
    
    # Header
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    
    # Title with coffee theme
    st.markdown(f"""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 class="modern-title">☕ {session_data['name']}</h1>
        <p style="font-size: 1.2rem; color: {colors['text_secondary']};">
            Professional Coffee Cupping Results
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Session overview cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        sample_count = len(session_data.get('samples', []))
        st.markdown(create_metric_card("Samples Cupped", f"{sample_count}"), 
                   unsafe_allow_html=True)
    
    with col2:
        cupper_name = session_data.get('cupper', 'Professional Cupper')
        if session_data.get('anonymous_mode'):
            cupper_name = 'Anonymous Taster'
        st.markdown(create_metric_card("Lead Cupper", cupper_name), 
                   unsafe_allow_html=True)
    
    with col3:
        protocol = session_data.get('protocol', 'SCA Standard')
        st.markdown(create_metric_card("Protocol", protocol), 
                   unsafe_allow_html=True)
    
    with col4:
        date = session_data.get('date', 'Recent')
        st.markdown(create_metric_card("Date", date), 
                   unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Check if session has scores
    if session_data.get('status') != 'Scored' or not session_data.get('scores'):
        st.warning("⏳ This cupping session hasn't been scored yet.")
        
        # Show samples information
        if session_data.get('samples'):
            st.markdown("### 📋 Sample Information")
            for i, sample in enumerate(session_data['samples']):
                with st.expander(f"☕ Sample {i+1}: {sample['name']}", expanded=True):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Origin:** {sample.get('origin', 'Not specified')}")
                        st.write(f"**Variety:** {sample.get('variety', 'Not specified')}")
                        st.write(f"**Process:** {sample.get('process', 'Not specified')}")
                    with col2:
                        st.write(f"**Altitude:** {sample.get('altitude', 'Not specified')}")
                        st.write(f"**Harvest Year:** {sample.get('harvest_year', 'Not specified')}")
        
        st.markdown("</div>", unsafe_allow_html=True)
        return
    
    # Overall scores section
    scores = session_data['scores']
    total_scores = [score.get('total', 0) for score in scores if score.get('total')]
    
    if total_scores:
        avg_total = sum(total_scores) / len(total_scores)
        highest_score = max(total_scores)
        lowest_score = min(total_scores)
        
        # Score overview
        st.markdown("### 🏆 Overall Results")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="score-container">
                <div style="text-align: center;">
                    <h2 style="color: {colors['primary']}; margin: 0;">{avg_total:.1f}</h2>
                    <p style="color: {colors['text_secondary']}; margin: 0;">Average Score</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            score_color = colors['success'] if highest_score >= 85 else colors['warning']
            st.markdown(f"""
            <div class="score-container">
                <div style="text-align: center;">
                    <h2 style="color: {score_color}; margin: 0;">{highest_score:.1f}</h2>
                    <p style="color: {colors['text_secondary']}; margin: 0;">Highest Score</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="score-container">
                <div style="text-align: center;">
                    <h2 style="color: {colors['primary']}; margin: 0;">{lowest_score:.1f}</h2>
                    <p style="color: {colors['text_secondary']}; margin: 0;">Lowest Score</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Radar chart for average scores
    st.markdown("### 📊 Sensory Profile")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        radar_fig = analytics.create_radar_chart(session_data, session_data['name'])
        st.plotly_chart(radar_fig, use_container_width=True)
    
    with col2:
        # Category insights
        session_insights = analytics.generate_session_insights(session_data)
        
        if session_insights:
            st.markdown("#### 🎯 Key Insights")
            
            if 'best_category' in session_insights:
                best_cat = session_insights['best_category']
                st.success(f"**Strongest:** {best_cat['name'].replace('_', ' ').title()} ({best_cat['score']:.1f})")
            
            if 'worst_category' in session_insights:
                worst_cat = session_insights['worst_category']
                st.warning(f"**Development Area:** {worst_cat['name'].replace('_', ' ').title()} ({worst_cat['score']:.1f})")
            
            if 'score_range' in session_insights:
                st.info(f"**Consistency:** {session_insights['score_range']:.1f} point range")
    
    # Individual sample results
    st.markdown("### 🔬 Individual Sample Results")
    
    for i, score in enumerate(scores):
        sample_name = score.get('sample_name', f'Sample {i+1}')
        total_score = score.get('total', 0)
        
        # Score color coding
        if total_score >= 90:
            score_color = colors['success']
            grade = "Outstanding"
            grade_icon = "🏆"
        elif total_score >= 85:
            score_color = colors['primary']
            grade = "Excellent"
            grade_icon = "⭐"
        elif total_score >= 80:
            score_color = colors['warning']
            grade = "Very Good"
            grade_icon = "👍"
        else:
            score_color = colors['error']
            grade = "Good"
            grade_icon = "👌"
        
        with st.expander(f"{grade_icon} {sample_name} - {total_score:.1f} points ({grade})", expanded=i==0):
            # Score breakdown
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Category scores table
                categories = ['Fragrance', 'Flavor', 'Aftertaste', 'Acidity', 'Body', 'Balance', 'Overall']
                category_keys = ['fragrance', 'flavor', 'aftertaste', 'acidity', 'body', 'balance', 'overall']
                
                score_data = []
                for cat, key in zip(categories, category_keys):
                    value = score.get(key, 0)
                    score_data.append([cat, f"{value:.1f}"])
                
                # Add special categories
                score_data.extend([
                    ['Uniformity', f"{score.get('uniformity', 0):.1f}"],
                    ['Clean Cup', f"{score.get('clean_cup', 0):.1f}"],
                    ['Sweetness', f"{score.get('sweetness', 0):.1f}"],
                    ['Defects', f"-{score.get('defects', 0):.1f}"]
                ])
                
                import pandas as pd
                df = pd.DataFrame(score_data, columns=['Category', 'Score'])
                st.dataframe(df, use_container_width=True, hide_index=True)
            
            with col2:
                # Gauge chart for total score
                fig = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=total_score,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "SCA Score"},
                    delta={'reference': 80},
                    gauge={
                        'axis': {'range': [None, 100]},
                        'bar': {'color': score_color},
                        'steps': [
                            {'range': [0, 75], 'color': "#f8d7da"},
                            {'range': [75, 80], 'color': "#fff3cd"},
                            {'range': [80, 85], 'color': "#d1ecf1"},
                            {'range': [85, 100], 'color': "#d4edda"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 90
                        }
                    }
                ))
                
                fig.update_layout(
                    height=300,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color=colors['text'])
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Tasting notes and flavors
            if score.get('notes') or score.get('selected_flavors'):
                st.markdown("#### 🍃 Tasting Notes")
                
                if score.get('notes'):
                    st.markdown(f"**Notes:** {score['notes']}")
                
                if score.get('selected_flavors'):
                    flavors = score['selected_flavors']
                    flavor_tags = " ".join([f"`{flavor}`" for flavor in flavors[:10]])
                    st.markdown(f"**Flavor Profile:** {flavor_tags}")
    
    # Session notes
    if session_data.get('session_notes'):
        st.markdown("### 📝 Session Notes")
        st.markdown(f"*{session_data['session_notes']}*")
    
    # Footer
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; padding: 2rem 0; color: {colors['text_secondary']};">
        <p>Generated by Coffee Cupping App Professional</p>
        <p style="font-size: 0.9rem;">{COPYRIGHT}</p>
        <p style="font-size: 0.8rem;">Want to create your own cupping sessions? 
        <a href="{st.secrets.get('app_url', '#')}" style="color: {colors['primary']};">Start cupping →</a></p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

def check_share_parameter():
    """Check if page was accessed via share parameter"""
    query_params = st.query_params
    return query_params.get('share', None)