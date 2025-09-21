"""
Analytics dashboard page for Coffee Cupping App
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from utils.analytics import analytics
from database.db_manager import db
from styles.themes import apply_custom_css, get_theme_colors, create_metric_card

def render_analytics_dashboard():
    """Render comprehensive analytics dashboard"""
    apply_custom_css()
    colors = get_theme_colors()
    
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    
    # Header
    st.markdown(f"""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 class="modern-title">📊 Analytics Dashboard</h1>
        <p style="font-size: 1.2rem; color: {colors['text_secondary']};">
            Community Insights & Cupping Trends
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get community trends
    with st.spinner("🔍 Analyzing community data..."):
        trends_data = analytics.get_community_trends()
    
    if not trends_data.get('total_sessions'):
        st.warning("📈 No cupping data available yet. Start cupping to see analytics!")
        st.markdown("</div>", unsafe_allow_html=True)
        return
    
    # Overview metrics
    st.markdown("### 🎯 Community Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(
            create_metric_card("Total Sessions", f"{trends_data['total_sessions']:,}"),
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            create_metric_card("Samples Cupped", f"{trends_data['total_samples']:,}"),
            unsafe_allow_html=True
        )
    
    with col3:
        avg_community_score = np.mean(trends_data.get('score_distribution', [0]))
        st.markdown(
            create_metric_card("Avg Community Score", f"{avg_community_score:.1f}"),
            unsafe_allow_html=True
        )
    
    with col4:
        flavor_count = len(trends_data.get('popular_flavors', {}))
        st.markdown(
            create_metric_card("Unique Flavors", f"{flavor_count:,}"),
            unsafe_allow_html=True
        )
    
    st.markdown("---")
    
    # Tabs for different analysis sections
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Score Analysis", 
        "🌍 Geographic Trends", 
        "🍃 Flavor Insights", 
        "⏰ Temporal Patterns",
        "🎖️ Quality Metrics"
    ])
    
    with tab1:
        render_score_analysis(trends_data, colors)
    
    with tab2:
        render_geographic_trends(trends_data, colors)
    
    with tab3:
        render_flavor_insights(trends_data, colors)
    
    with tab4:
        render_temporal_patterns(trends_data, colors)
    
    with tab5:
        render_quality_metrics(trends_data, colors)
    
    # Footer
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; padding: 1rem 0; color: {colors['text_secondary']};">
        <p>Data updates in real-time as new cupping sessions are completed</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

def render_score_analysis(trends_data, colors):
    """Render score analysis section"""
    st.markdown("#### 📊 Score Distribution & Category Performance")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Score distribution histogram
        score_dist_fig = analytics.create_score_distribution(trends_data)
        st.plotly_chart(score_dist_fig, use_container_width=True)
    
    with col2:
        # Category comparison
        category_fig = analytics.create_category_comparison(trends_data)
        st.plotly_chart(category_fig, use_container_width=True)
    
    # Score statistics
    st.markdown("#### 📈 Statistical Summary")
    
    scores = trends_data.get('score_distribution', [])
    if scores:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Mean Score", f"{np.mean(scores):.1f}")
        with col2:
            st.metric("Median Score", f"{np.median(scores):.1f}")
        with col3:
            st.metric("Std Deviation", f"{np.std(scores):.1f}")
        with col4:
            percentile_90 = np.percentile(scores, 90)
            st.metric("90th Percentile", f"{percentile_90:.1f}")

def render_geographic_trends(trends_data, colors):
    """Render geographic analysis section"""
    st.markdown("#### 🌍 Origin Analysis")
    
    top_origins = trends_data.get('top_origins', {})
    
    if top_origins:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Origins bar chart
            origins_df = pd.DataFrame(list(top_origins.items()), columns=['Origin', 'Count'])
            fig = px.bar(
                origins_df.head(10), 
                x='Count', 
                y='Origin',
                orientation='h',
                title="Top Coffee Origins",
                color='Count',
                color_continuous_scale='Browns'
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color=colors['text'])
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Origins summary
            st.markdown("**Origin Insights:**")
            for i, (origin, count) in enumerate(list(top_origins.items())[:5], 1):
                percentage = (count / sum(top_origins.values())) * 100
                st.write(f"{i}. **{origin}** - {count} samples ({percentage:.1f}%)")
    else:
        st.info("No origin data available yet.")

def render_flavor_insights(trends_data, colors):
    """Render flavor analysis section"""
    st.markdown("#### 🍃 Flavor Profile Analysis")
    
    popular_flavors = trends_data.get('popular_flavors', {})
    
    if popular_flavors:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Popular flavors chart
            flavor_fig = analytics.create_flavor_popularity_chart(trends_data)
            st.plotly_chart(flavor_fig, use_container_width=True)
        
        with col2:
            # Flavor categories analysis
            st.markdown("**Flavor Categories:**")
            
            # Group flavors by categories
            from config import FLAVOR_CATEGORIES
            category_counts = {}
            
            for flavor, count in popular_flavors.items():
                for category, data in FLAVOR_CATEGORIES.items():
                    for subcat, flavors in data['subcategories'].items():
                        if flavor in flavors:
                            category_counts[category] = category_counts.get(category, 0) + count
                            break
            
            # Display category summary
            for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / sum(category_counts.values())) * 100
                st.write(f"**{category}:** {count} ({percentage:.1f}%)")
        
        # Flavor trends over time (if temporal data available)
        st.markdown("#### 📅 Flavor Trends")
        
        # Create a simple flavor trend visualization
        flavor_trend_data = []
        for flavor, count in list(popular_flavors.items())[:8]:
            flavor_trend_data.append({
                'Flavor': flavor,
                'Popularity': count,
                'Category': 'Popular'
            })
        
        if flavor_trend_data:
            df = pd.DataFrame(flavor_trend_data)
            fig = px.treemap(
                df, 
                path=['Category', 'Flavor'], 
                values='Popularity',
                title="Flavor Popularity Treemap",
                color='Popularity',
                color_continuous_scale='Browns'
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color=colors['text'])
            )
            st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.info("No flavor data available yet.")

def render_temporal_patterns(trends_data, colors):
    """Render temporal analysis section"""
    st.markdown("#### ⏰ Cupping Activity Over Time")
    
    temporal_data = trends_data.get('temporal_trends', [])
    
    if temporal_data:
        # Temporal trends chart
        temporal_fig = analytics.create_temporal_trends(trends_data)
        st.plotly_chart(temporal_fig, use_container_width=True)
        
        # Activity summary
        st.markdown("#### 📅 Activity Summary")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            recent_sessions = len([t for t in temporal_data if t['month'] >= (datetime.now() - timedelta(days=90)).strftime('%Y-%m')])
            st.metric("Sessions (Last 3 Months)", recent_sessions)
        
        with col2:
            if temporal_data:
                avg_monthly_sessions = np.mean([t['sessions_count'] for t in temporal_data])
                st.metric("Avg Monthly Sessions", f"{avg_monthly_sessions:.1f}")
        
        with col3:
            if temporal_data:
                latest_avg = temporal_data[-1]['average_score'] if temporal_data else 0
                previous_avg = temporal_data[-2]['average_score'] if len(temporal_data) > 1 else 0
                trend = "📈" if latest_avg > previous_avg else "📉" if latest_avg < previous_avg else "➡️"
                st.metric("Score Trend", f"{trend} {latest_avg:.1f}")
    
    else:
        st.info("No temporal data available yet.")

def render_quality_metrics(trends_data, colors):
    """Render quality metrics section"""
    st.markdown("#### 🎖️ Quality Assessment")
    
    scores = trends_data.get('score_distribution', [])
    
    if scores:
        # Quality grade distribution
        grade_distribution = {
            'Outstanding (90+)': len([s for s in scores if s >= 90]),
            'Excellent (85-89)': len([s for s in scores if 85 <= s < 90]),
            'Very Good (80-84)': len([s for s in scores if 80 <= s < 85]),
            'Good (75-79)': len([s for s in scores if 75 <= s < 80]),
            'Fair (<75)': len([s for s in scores if s < 75])
        }
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Pie chart of quality grades
            grades_df = pd.DataFrame(list(grade_distribution.items()), columns=['Grade', 'Count'])
            grades_df = grades_df[grades_df['Count'] > 0]  # Remove empty grades
            
            fig = px.pie(
                grades_df, 
                values='Count', 
                names='Grade',
                title="Quality Grade Distribution",
                color_discrete_sequence=['#28a745', '#17a2b8', '#ffc107', '#fd7e14', '#dc3545']
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color=colors['text'])
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Quality metrics
            st.markdown("**Quality Insights:**")
            
            total_samples = len(scores)
            excellent_and_above = len([s for s in scores if s >= 85])
            specialty_grade = len([s for s in scores if s >= 80])
            
            if total_samples > 0:
                st.metric("Specialty Grade (%)", f"{(specialty_grade/total_samples)*100:.1f}%")
                st.metric("Excellent+ (%)", f"{(excellent_and_above/total_samples)*100:.1f}%")
                
                # Quality trend
                if len(scores) >= 10:
                    recent_avg = np.mean(scores[-10:])
                    overall_avg = np.mean(scores)
                    improvement = recent_avg - overall_avg
                    
                    trend_text = "📈 Improving" if improvement > 0.5 else "📉 Declining" if improvement < -0.5 else "➡️ Stable"
                    st.metric("Quality Trend", trend_text, f"{improvement:+.1f} pts")
        
        # Protocol effectiveness
        st.markdown("#### ⚙️ Protocol Analysis")
        
        protocols = trends_data.get('protocol_usage', {})
        if protocols:
            protocol_df = pd.DataFrame(list(protocols.items()), columns=['Protocol', 'Usage'])
            
            fig = px.bar(
                protocol_df,
                x='Protocol',
                y='Usage',
                title="Cupping Protocol Usage",
                color='Usage',
                color_continuous_scale='Browns'
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color=colors['text'])
            )
            st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.info("No quality data available yet.")