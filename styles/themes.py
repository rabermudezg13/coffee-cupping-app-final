"""
Modern themes and styling for Coffee Cupping App
"""
import streamlit as st

def get_theme_config():
    """Get current theme configuration"""
    if 'theme_mode' not in st.session_state:
        st.session_state.theme_mode = 'light'
    return st.session_state.theme_mode

def toggle_theme():
    """Toggle between light and dark theme"""
    current = get_theme_config()
    st.session_state.theme_mode = 'dark' if current == 'light' else 'light'

def get_theme_colors(theme_mode=None):
    """Get color palette for current theme"""
    if theme_mode is None:
        theme_mode = get_theme_config()
    
    if theme_mode == 'dark':
        return {
            'background': '#1E1E1E',
            'surface': '#2D2D2D',
            'primary': '#D4AF37',
            'secondary': '#8B4513',
            'text': '#FFFFFF',
            'text_secondary': '#CCCCCC',
            'accent': '#FF6B6B',
            'success': '#4CAF50',
            'warning': '#FF9800',
            'error': '#F44336',
            'coffee_card': 'linear-gradient(145deg, #2D2D2D, #3D3D3D)',
            'shadow': 'rgba(255,255,255,0.1)'
        }
    else:
        return {
            'background': '#FFFFFF',
            'surface': '#F5F5F5',
            'primary': '#8B4513',
            'secondary': '#D2B48C',
            'text': '#333333',
            'text_secondary': '#666666',
            'accent': '#FF6B6B',
            'success': '#4CAF50',
            'warning': '#FF9800',
            'error': '#F44336',
            'coffee_card': 'linear-gradient(145deg, #F5F5DC, #E6E6D3)',
            'shadow': 'rgba(0,0,0,0.1)'
        }

def apply_custom_css():
    """Apply modern CSS styling with theme support"""
    theme_mode = get_theme_config()
    colors = get_theme_colors(theme_mode)
    
    css = f"""
    <style>
    /* Hide Streamlit branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    [data-testid="stToolbar"] {{display: none;}}
    [data-testid="stDecoration"] {{display: none;}}
    [data-testid="stHeader"] {{display: none;}}
    
    /* Main app container */
    .main .block-container {{
        padding: 1rem 2rem;
        max-width: 1200px;
    }}
    
    /* Modern coffee card styling */
    .coffee-card {{
        background: {colors['coffee_card']};
        padding: 1.5rem;
        border-radius: 20px;
        border-left: 5px solid {colors['primary']};
        margin: 1rem 0;
        box-shadow: 0 8px 32px {colors['shadow']};
        backdrop-filter: blur(4px);
        transition: all 0.3s ease;
    }}
    
    .coffee-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 12px 40px {colors['shadow']};
    }}
    
    /* Modern metric cards */
    .metric-card {{
        background: {colors['surface']};
        padding: 1.2rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 20px {colors['shadow']};
        border: 1px solid {colors['secondary']}40;
        transition: all 0.3s ease;
    }}
    
    .metric-card:hover {{
        transform: scale(1.02);
        box-shadow: 0 6px 25px {colors['shadow']};
    }}
    
    /* Score visualization */
    .score-container {{
        background: {colors['coffee_card']};
        padding: 2rem;
        border-radius: 20px;
        margin: 1rem 0;
        box-shadow: 0 8px 32px {colors['shadow']};
    }}
    
    /* Modern buttons */
    .stButton > button {{
        background: linear-gradient(45deg, {colors['primary']}, {colors['secondary']});
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px {colors['shadow']};
    }}
    
    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 20px {colors['shadow']};
    }}
    
    /* Responsive design */
    @media (max-width: 768px) {{
        .main .block-container {{
            padding: 1rem;
        }}
        
        .coffee-card {{
            padding: 1rem;
            margin: 0.5rem 0;
        }}
        
        .metric-card {{
            padding: 1rem;
        }}
    }}
    
    /* Dark mode specific adjustments */
    {"" if theme_mode == 'light' else f"""
    .stApp {{
        background-color: {colors['background']};
        color: {colors['text']};
    }}
    
    .stSelectbox > div > div {{
        background-color: {colors['surface']};
        color: {colors['text']};
    }}
    
    .stTextInput > div > div > input {{
        background-color: {colors['surface']};
        color: {colors['text']};
        border: 1px solid {colors['secondary']};
    }}
    """}
    
    /* Modern animations */
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(20px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    
    .fade-in {{
        animation: fadeIn 0.6s ease-out;
    }}
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {{
        width: 8px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: {colors['surface']};
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: {colors['primary']};
        border-radius: 4px;
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: {colors['secondary']};
    }}
    
    /* Modern typography */
    .modern-title {{
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(45deg, {colors['primary']}, {colors['accent']});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }}
    
    .section-header {{
        font-size: 1.5rem;
        font-weight: 600;
        color: {colors['primary']};
        margin: 1.5rem 0 1rem 0;
        border-bottom: 2px solid {colors['primary']};
        padding-bottom: 0.5rem;
    }}
    
    /* Share button styling */
    .share-button {{
        background: linear-gradient(45deg, #1DA1F2, #1991DB);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        margin: 0.25rem;
    }}
    
    .share-button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(29, 161, 242, 0.4);
    }}
    
    /* Anonymous mode toggle */
    .anonymous-toggle {{
        background: {colors['surface']};
        border: 2px solid {colors['primary']};
        border-radius: 15px;
        padding: 1rem;
        margin: 1rem 0;
    }}
    </style>
    """
    
    st.markdown(css, unsafe_allow_html=True)

def render_theme_toggle():
    """Render theme toggle button in sidebar"""
    current_theme = get_theme_config()
    theme_icon = "🌙" if current_theme == "light" else "☀️"
    theme_text = "Dark" if current_theme == "light" else "Light"
    
    if st.sidebar.button(f"{theme_icon} {theme_text} Mode"):
        toggle_theme()
        st.rerun()

def create_metric_card(title, value, delta=None, delta_color="normal"):
    """Create a modern metric card"""
    colors = get_theme_colors()
    
    delta_html = ""
    if delta:
        delta_color_code = colors['success'] if delta_color == 'normal' else colors['error']
        delta_html = f'<div style="color: {delta_color_code}; font-size: 0.8rem; margin-top: 0.5rem;">{delta}</div>'
    
    card_html = f"""
    <div class="metric-card">
        <div style="font-size: 0.9rem; color: {colors['text_secondary']}; margin-bottom: 0.5rem;">{title}</div>
        <div style="font-size: 2rem; font-weight: 700; color: {colors['primary']};">{value}</div>
        {delta_html}
    </div>
    """
    
    return card_html