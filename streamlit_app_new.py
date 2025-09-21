"""
Modern Coffee Cupping App - Professional
Enhanced with sharing, analytics, and modern UI
"""
import streamlit as st
from datetime import datetime, date
import json
import os
import sys
import uuid

# Add current directory to path for imports
sys.path.append(os.path.dirname(__file__))

# Import our modules
from config import *
from styles.themes import apply_custom_css, render_theme_toggle, get_theme_colors, create_metric_card
from database.db_manager import db
from utils.analytics import analytics
from utils.sharing import sharing_manager
from pages.public_cupping import render_public_cupping_page, check_share_parameter
from pages.analytics_dashboard import render_analytics_dashboard

# Page configuration
st.set_page_config(
    page_title=APP_NAME,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Main application function"""
    # Apply custom styling
    apply_custom_css()
    colors = get_theme_colors()
    
    # Check if accessing shared cupping
    share_id = check_share_parameter()
    if share_id:
        render_public_cupping_page(share_id)
        return
    
    # Sidebar navigation
    render_sidebar()
    
    # Main content area
    if 'current_user' not in st.session_state:
        render_login_page()
    else:
        render_main_app()

def render_sidebar():
    """Render sidebar navigation"""
    with st.sidebar:
        st.markdown(f"# {APP_ICON} Coffee Cupping")
        st.markdown("**Professional Edition**")
        
        # Theme toggle
        render_theme_toggle()
        
        st.markdown("---")
        
        # Navigation
        if 'current_user' in st.session_state:
            st.markdown(f"👋 Welcome, **{st.session_state.current_user}**")
            
            # Navigation menu
            page = st.selectbox(
                "🧭 Navigate",
                ["🏠 Dashboard", "☕ New Cupping", "📋 My Sessions", "📊 Analytics", "⚙️ Settings"],
                key="nav_select"
            )
            st.session_state.current_page = page
            
            st.markdown("---")
            
            # Quick stats
            render_quick_stats()
            
            if st.button("🚪 Logout"):
                logout_user()
        else:
            st.info("Please login to access the app")

def render_quick_stats():
    """Render quick statistics in sidebar"""
    try:
        # Get user's sessions
        data = db.load_json_data()
        user_sessions = [s for s in data.get('cupping_sessions', []) 
                        if s.get('user_email') == st.session_state.get('current_user')]
        
        completed_sessions = len([s for s in user_sessions if s.get('status') == 'Scored'])
        total_samples = sum(len(s.get('samples', [])) for s in user_sessions)
        
        st.markdown("### 📈 Quick Stats")
        st.metric("Sessions", len(user_sessions))
        st.metric("Completed", completed_sessions)
        st.metric("Samples", total_samples)
        
        if completed_sessions > 0:
            # Calculate average score
            all_scores = []
            for session in user_sessions:
                if session.get('scores'):
                    for score in session['scores']:
                        if score.get('total'):
                            all_scores.append(score['total'])
            
            if all_scores:
                avg_score = sum(all_scores) / len(all_scores)
                st.metric("Avg Score", f"{avg_score:.1f}")
    
    except Exception as e:
        st.error(f"Error loading stats: {e}")

def render_login_page():
    """Render modern login page"""
    colors = get_theme_colors()
    
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    
    # Centered login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown(f"""
        <div style="text-align: center; padding: 3rem 0;">
            <h1 class="modern-title">{APP_ICON} Coffee Cupping Professional</h1>
            <p style="font-size: 1.2rem; color: {colors['text_secondary']}; margin-bottom: 2rem;">
                Advanced cupping analysis with community insights
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Login form
        st.markdown("### 🔐 Login")
        
        with st.form("login_form"):
            email = st.text_input("📧 Email", placeholder="demo@coffee.com")
            password = st.text_input("🔒 Password", type="password", placeholder="demo123")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                login_button = st.form_submit_button("🚀 Login", use_container_width=True)
            with col2:
                # Anonymous mode toggle
                anonymous_mode = st.checkbox("🕶️ Anonymous Mode", 
                                           help="Hide your identity in shared results")
            
            if login_button:
                if authenticate_user(email, password):
                    st.session_state.current_user = email
                    st.session_state.anonymous_mode = anonymous_mode
                    st.success("✅ Login successful!")
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials")
        
        # Demo credentials info
        st.info(f"""
        **Demo Credentials:**  
        📧 Email: `{DEMO_CREDENTIALS['email']}`  
        🔒 Password: `{DEMO_CREDENTIALS['password']}`
        """)
        
        # Features preview
        st.markdown("---")
        st.markdown("### ✨ Features")
        
        features = [
            "🔗 **Share Results** - Generate unique URLs for public viewing",
            "🕶️ **Anonymous Mode** - Hide your identity when sharing",
            "📊 **Advanced Analytics** - Community trends and insights",
            "🎨 **Modern UI** - Dark/Light themes, responsive design",
            "📱 **Social Sharing** - Export to social media platforms",
            "⚡ **Real-time Updates** - Live scoring and calculations"
        ]
        
        for feature in features:
            st.markdown(feature)
    
    st.markdown("</div>", unsafe_allow_html=True)

def authenticate_user(email: str, password: str) -> bool:
    """Authenticate user login"""
    # For demo, use hardcoded credentials
    # In production, this would check against a secure database
    return email == DEMO_CREDENTIALS['email'] and password == DEMO_CREDENTIALS['password']

def logout_user():
    """Logout current user"""
    keys_to_remove = ['current_user', 'anonymous_mode', 'current_page']
    for key in keys_to_remove:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

def render_main_app():
    """Render main application interface"""
    page = st.session_state.get('current_page', '🏠 Dashboard')
    
    if page == '🏠 Dashboard':
        render_dashboard()
    elif page == '☕ New Cupping':
        render_new_cupping()
    elif page == '📋 My Sessions':
        render_my_sessions()
    elif page == '📊 Analytics':
        render_analytics_dashboard()
    elif page == '⚙️ Settings':
        render_settings()

def render_dashboard():
    """Render dashboard page"""
    colors = get_theme_colors()
    
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    
    # Welcome header
    user_name = st.session_state.current_user.split('@')[0].title()
    current_time = datetime.now().strftime("%B %d, %Y")
    
    st.markdown(f"""
    <div style="padding: 2rem 0;">
        <h1 class="modern-title">Welcome back, {user_name}! {APP_ICON}</h1>
        <p style="font-size: 1.1rem; color: {colors['text_secondary']};">{current_time}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick actions
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("☕ Start New Cupping", use_container_width=True):
            st.session_state.current_page = '☕ New Cupping'
            st.rerun()
    
    with col2:
        if st.button("📋 View My Sessions", use_container_width=True):
            st.session_state.current_page = '📋 My Sessions'
            st.rerun()
    
    with col3:
        if st.button("📊 Analytics Dashboard", use_container_width=True):
            st.session_state.current_page = '📊 Analytics'
            st.rerun()
    
    with col4:
        if st.button("🔗 Share Results", use_container_width=True):
            st.session_state.current_page = '📋 My Sessions'
            st.rerun()
    
    st.markdown("---")
    
    # Recent activity and stats
    col1, col2 = st.columns([2, 1])
    
    with col1:
        render_recent_activity()
    
    with col2:
        render_dashboard_stats()
    
    st.markdown("</div>", unsafe_allow_html=True)

def render_recent_activity():
    """Render recent cupping activity"""
    st.markdown("### 🕒 Recent Activity")
    
    try:
        data = db.load_json_data()
        user_sessions = [s for s in data.get('cupping_sessions', []) 
                        if s.get('user_email') == st.session_state.get('current_user')]
        
        # Sort by date (most recent first)
        user_sessions.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        if user_sessions:
            for session in user_sessions[:5]:  # Show last 5 sessions
                status_icon = "✅" if session.get('status') == 'Scored' else "⏳"
                date_str = session.get('date', 'Unknown date')
                sample_count = len(session.get('samples', []))
                
                with st.expander(f"{status_icon} {session['name']} - {date_str}"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"**Samples:** {sample_count}")
                        st.write(f"**Status:** {session.get('status', 'Unknown')}")
                        if session.get('cupper'):
                            st.write(f"**Cupper:** {session['cupper']}")
                    
                    with col2:
                        if session.get('share_id'):
                            if st.button("🔗 Share", key=f"quick_share_{session.get('share_id')}"):
                                st.info(f"Share URL: {sharing_manager.generate_share_url(session['share_id'])}")
        else:
            st.info("No cupping sessions yet. Start your first cupping!")
    
    except Exception as e:
        st.error(f"Error loading recent activity: {e}")

def render_dashboard_stats():
    """Render dashboard statistics"""
    st.markdown("### 📊 Your Statistics")
    
    try:
        data = db.load_json_data()
        user_sessions = [s for s in data.get('cupping_sessions', []) 
                        if s.get('user_email') == st.session_state.get('current_user')]
        
        # Calculate stats
        total_sessions = len(user_sessions)
        completed_sessions = len([s for s in user_sessions if s.get('status') == 'Scored'])
        total_samples = sum(len(s.get('samples', [])) for s in user_sessions)
        
        # Score statistics
        all_scores = []
        for session in user_sessions:
            if session.get('scores'):
                for score in session['scores']:
                    if score.get('total'):
                        all_scores.append(score['total'])
        
        avg_score = sum(all_scores) / len(all_scores) if all_scores else 0
        highest_score = max(all_scores) if all_scores else 0
        
        # Display metrics
        st.metric("Total Sessions", total_sessions)
        st.metric("Completed", completed_sessions)
        st.metric("Samples Cupped", total_samples)
        
        if all_scores:
            st.metric("Average Score", f"{avg_score:.1f}")
            st.metric("Highest Score", f"{highest_score:.1f}")
        
        # Progress towards next milestone
        st.markdown("### 🎯 Progress")
        next_milestone = ((total_sessions // 10) + 1) * 10
        progress = total_sessions / next_milestone
        st.progress(progress)
        st.caption(f"{total_sessions}/{next_milestone} sessions to next milestone")
    
    except Exception as e:
        st.error(f"Error calculating statistics: {e}")

def render_new_cupping():
    """Render new cupping session creation"""
    from components.cupping_interface import render_enhanced_cupping_interface
    render_enhanced_cupping_interface()

def render_my_sessions():
    """Render user's cupping sessions with enhanced sharing"""
    st.markdown("### 📋 My Cupping Sessions")
    
    try:
        data = db.load_json_data()
        user_sessions = [s for s in data.get('cupping_sessions', []) 
                        if s.get('user_email') == st.session_state.get('current_user')]
        
        if not user_sessions:
            st.info("No cupping sessions yet. Create your first session!")
            return
        
        # Sort sessions
        sort_option = st.selectbox("Sort by", ["Most Recent", "Oldest", "Name", "Status"])
        
        if sort_option == "Most Recent":
            user_sessions.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        elif sort_option == "Oldest":
            user_sessions.sort(key=lambda x: x.get('created_at', ''))
        elif sort_option == "Name":
            user_sessions.sort(key=lambda x: x.get('name', ''))
        elif sort_option == "Status":
            user_sessions.sort(key=lambda x: x.get('status', ''))
        
        # Display sessions
        for i, session in enumerate(user_sessions):
            status_color = "#28a745" if session.get('status') == 'Scored' else "#ffc107"
            status_icon = "✅" if session.get('status') == 'Scored' else "⏳"
            
            with st.expander(f"{status_icon} {session['name']} - {session.get('date', 'No date')}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**Status:** {session.get('status', 'Unknown')}")
                    st.write(f"**Samples:** {len(session.get('samples', []))}")
                    st.write(f"**Protocol:** {session.get('protocol', 'Unknown')}")
                    if session.get('cupper'):
                        cupper_display = session['cupper']
                        if session.get('anonymous_mode'):
                            cupper_display = "Anonymous Taster"
                        st.write(f"**Cupper:** {cupper_display}")
                
                with col2:
                    # Action buttons
                    if session.get('status') == 'Scored':
                        if st.button(f"📊 View Results", key=f"view_{i}"):
                            # Show detailed results
                            render_session_results(session)
                    
                    if session.get('share_id'):
                        if st.button(f"🔗 Share Session", key=f"share_{i}"):
                            st.session_state[f"show_sharing_{i}"] = True
                
                # Sharing interface
                if st.session_state.get(f"show_sharing_{i}"):
                    st.markdown("---")
                    sharing_manager.render_sharing_interface(session, session['share_id'])
    
    except Exception as e:
        st.error(f"Error loading sessions: {e}")

def render_session_results(session):
    """Render detailed session results"""
    if not session.get('scores'):
        st.warning("No scores available for this session.")
        return
    
    # Create radar chart
    radar_fig = analytics.create_radar_chart(session, session['name'])
    st.plotly_chart(radar_fig, use_container_width=True)
    
    # Show individual scores
    for score in session['scores']:
        st.write(f"**{score['sample_name']}:** {score.get('total', 0):.1f} points")

def render_settings():
    """Render settings page"""
    st.markdown("### ⚙️ Settings")
    
    # Theme settings
    st.markdown("#### 🎨 Appearance")
    current_theme = st.session_state.get('theme_mode', 'light')
    st.write(f"Current theme: **{current_theme.title()}**")
    
    # Anonymous mode default
    st.markdown("#### 🕶️ Privacy")
    default_anonymous = st.checkbox(
        "Default to anonymous mode",
        value=st.session_state.get('default_anonymous', False),
        help="Always start new sessions in anonymous mode"
    )
    st.session_state.default_anonymous = default_anonymous
    
    # Export settings
    st.markdown("#### 📥 Export")
    if st.button("📊 Export All My Data"):
        export_user_data()

def export_user_data():
    """Export user's cupping data"""
    try:
        data = db.load_json_data()
        user_sessions = [s for s in data.get('cupping_sessions', []) 
                        if s.get('user_email') == st.session_state.get('current_user')]
        
        export_data = {
            'user': st.session_state.current_user,
            'exported_at': datetime.now().isoformat(),
            'sessions': user_sessions
        }
        
        st.download_button(
            label="📥 Download Data (JSON)",
            data=json.dumps(export_data, indent=2),
            file_name=f"cupping_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    except Exception as e:
        st.error(f"Error exporting data: {e}")

if __name__ == "__main__":
    main()