import streamlit as st
from datetime import datetime, date
import json
import os
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.units import inch
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from matplotlib.patches import Wedge
import tempfile

# Page configuration
st.set_page_config(
    page_title="Coffee Cupping App - Professional",
    page_icon="☕",
    layout="wide"
)

# Hide Streamlit branding
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stToolbar"] {display: none;}
    [data-testid="stDecoration"] {display: none;}
    [data-testid="stHeader"] {display: none;}
    
    .coffee-card {
        background: linear-gradient(145deg, #F5F5DC, #E6E6D3);
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 5px solid #8B4513;
        margin: 1rem 0;
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Database functions for persistence
DATA_FILE = "coffee_app_data.json"

def load_data():
    """Load data from JSON file"""
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Validate data structure
                if not isinstance(data, dict):
                    return {"users": {}, "sessions": [], "reviews": []}
                return {
                    "users": data.get("users", {}),
                    "sessions": data.get("sessions", []),
                    "reviews": data.get("reviews", [])
                }
    except Exception as e:
        # Don't show error to user, just use defaults
        pass
    return {"users": {}, "sessions": [], "reviews": []}

def save_data():
    """Save data to JSON file - handles Streamlit Cloud restrictions"""
    try:
        data = {
            "users": st.session_state.get('registered_users', {}),
            "sessions": st.session_state.get('cupping_sessions', []),
            "reviews": st.session_state.get('coffee_reviews', []),
            "coffee_shops": st.session_state.get('coffee_shops', [])
        }
        
        # Validate data before saving
        if not isinstance(data["users"], dict):
            data["users"] = {}
        if not isinstance(data["sessions"], list):
            data["sessions"] = []
        if not isinstance(data["reviews"], list):
            data["reviews"] = []
        if not isinstance(data["coffee_shops"], list):
            data["coffee_shops"] = []
            
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        # Silently fail on Streamlit Cloud (read-only filesystem)
        # Data will persist in session state during the session
        return False

def init_data():
    """Initialize data from file on app start"""
    if 'data_loaded' not in st.session_state:
        # Try to load from file, but don't fail if it doesn't work
        try:
            data = load_data()
        except:
            data = {"users": {}, "sessions": [], "reviews": [], "coffee_shops": []}
        
        st.session_state.registered_users = data.get("users", {})
        st.session_state.cupping_sessions = data.get("sessions", [])
        st.session_state.coffee_reviews = data.get("reviews", [])
        st.session_state.coffee_shops = data.get("coffee_shops", [])
        st.session_state.data_loaded = True
    
    # Always ensure these exist as lists/dicts with some demo data
    if 'registered_users' not in st.session_state:
        st.session_state.registered_users = {}
    if 'cupping_sessions' not in st.session_state:
        st.session_state.cupping_sessions = []
    if 'coffee_reviews' not in st.session_state:
        st.session_state.coffee_reviews = []
    if 'coffee_shops' not in st.session_state:
        st.session_state.coffee_shops = []
    
    # Add some demo users if none exist (for persistence demo)
    if not st.session_state.registered_users:
        st.session_state.registered_users = {
            "test@coffee.com": {
                "name": "Coffee Tester",
                "password": "test123",
                "company": "Coffee Co",
                "role": "Q Grader",
                "experience": "Expert",
                "created": "2025-01-01 00:00"
            },
            "user@example.com": {
                "name": "Coffee User",
                "password": "user123", 
                "company": "Independent",
                "role": "Coffee Enthusiast",
                "experience": "Intermediate",
                "created": "2025-01-01 00:00"
            }
        }

def get_language():
    if 'language' not in st.session_state:
        st.session_state.language = 'en'
    return st.session_state.language

def create_score_visualization(scores):
    """Create a visual representation of cupping scores"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    
    # Score radar chart
    categories = ['Fragrance', 'Flavor', 'Aftertaste', 'Acidity', 'Body', 'Balance', 'Overall']
    
    # Create radar chart for first sample (or average if multiple)
    if scores:
        if len(scores) == 1:
            values = [scores[0][cat.lower()] for cat in categories]
            sample_name = scores[0]['sample_name']
        else:
            # Average of all samples
            values = []
            for cat in categories:
                avg_val = sum(score[cat.lower()] for score in scores) / len(scores)
                values.append(avg_val)
            sample_name = f"Average of {len(scores)} samples"
        
        # Number of variables
        N = len(categories)
        
        # Compute angle of each axis
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1]  # Complete the circle
        
        # Add values for completion
        values += values[:1]
        
        # Plot
        ax1.set_theta_offset(np.pi / 2)
        ax1.set_theta_direction(-1)
        ax1.plot(angles, values, 'o-', linewidth=2, label=sample_name, color='#8B4513')
        ax1.fill(angles, values, alpha=0.25, color='#D2B48C')
        ax1.set_xticks(angles[:-1])
        ax1.set_xticklabels(categories)
        ax1.set_ylim(6, 10)
        ax1.set_title('SCA Cupping Scores', size=14, fontweight='bold', pad=20)
        ax1.grid(True)
        
        # Add score labels
        for angle, value, category in zip(angles[:-1], values[:-1], categories):
            ax1.text(angle, value + 0.1, f'{value:.1f}', 
                    ha='center', va='center', fontsize=9, fontweight='bold')
    
    # Overall score gauge
    if scores:
        total_scores = [score['total'] for score in scores]
        avg_total = sum(total_scores) / len(total_scores)
        
        # Create gauge chart
        ax2.set_xlim(-1.5, 1.5)
        ax2.set_ylim(-1.5, 1.5)
        ax2.set_aspect('equal')
        
        # Create gauge sections
        colors_gauge = ['#dc3545', '#fd7e14', '#ffc107', '#17a2b8', '#28a745']
        labels = ['Fair\n(<75)', 'Good\n(75-79)', 'Very Good\n(80-84)', 'Excellent\n(85-89)', 'Outstanding\n(90+)']
        ranges = [75, 80, 85, 90, 100]
        
        for i, (color, label, end_range) in enumerate(zip(colors_gauge, labels, ranges)):
            start_angle = 180 - (i * 36)
            end_angle = 180 - ((i + 1) * 36)
            
            wedge = Wedge((0, 0), 1, end_angle, start_angle, 
                         facecolor=color, alpha=0.7, edgecolor='white', linewidth=2)
            ax2.add_patch(wedge)
            
            # Add labels
            mid_angle = np.radians((start_angle + end_angle) / 2)
            label_x = 0.7 * np.cos(mid_angle)
            label_y = 0.7 * np.sin(mid_angle)
            ax2.text(label_x, label_y, label, ha='center', va='center', 
                    fontsize=8, fontweight='bold')
        
        # Add needle
        score_angle = 180 - ((avg_total - 70) / 30 * 180)
        needle_angle = np.radians(score_angle)
        needle_x = 0.8 * np.cos(needle_angle)
        needle_y = 0.8 * np.sin(needle_angle)
        
        ax2.arrow(0, 0, needle_x, needle_y, head_width=0.05, head_length=0.1,
                 fc='black', ec='black', linewidth=3)
        
        # Add score text
        ax2.text(0, -0.3, f'{avg_total:.1f}', ha='center', va='center',
                fontsize=20, fontweight='bold', color='#8B4513')
        ax2.text(0, -0.5, 'SCA Score', ha='center', va='center',
                fontsize=12, fontweight='bold')
        
        ax2.set_title('Overall Score', size=14, fontweight='bold', pad=20)
        ax2.axis('off')
    
    plt.tight_layout()
    
    # Save to temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png', dir=tempfile.gettempdir())
    plt.savefig(temp_file.name, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return temp_file.name

def create_flavor_wheel(selected_flavors):
    """Create a beautiful flavor wheel visualization"""
    fig, ax = plt.subplots(figsize=(10, 10))
    
    # SCA Flavor categories with colors
    flavor_categories = {
        'Fruity': {
            'color': '#FF6B6B',
            'subcategories': {
                'Citrus': ['Grapefruit', 'Orange', 'Lemon', 'Lime'],
                'Berry': ['Blackberry', 'Raspberry', 'Blueberry', 'Strawberry'],
                'Stone Fruit': ['Peach', 'Apricot', 'Plum', 'Cherry'],
                'Tropical': ['Pineapple', 'Mango', 'Papaya', 'Coconut']
            }
        },
        'Floral': {
            'color': '#FF69B4',
            'subcategories': {
                'Floral': ['Rose', 'Jasmine', 'Lavender', 'Chamomile'],
                'Tea-like': ['Black Tea', 'Earl Grey']
            }
        },
        'Sweet': {
            'color': '#FFD700',
            'subcategories': {
                'Brown Sugar': ['Molasses', 'Maple Syrup', 'Caramel', 'Honey'],
                'Vanilla': ['Vanilla'],
                'Chocolate': ['Dark Chocolate', 'Milk Chocolate']
            }
        },
        'Nutty': {
            'color': '#DEB887',
            'subcategories': {
                'Tree Nuts': ['Almond', 'Hazelnut', 'Walnut', 'Pecan'],
                'Legumes': ['Peanut']
            }
        },
        'Green': {
            'color': '#90EE90',
            'subcategories': {
                'Fresh': ['Green', 'Underripe'],
                'Dried': ['Hay', 'Herb-like']
            }
        },
        'Roasted': {
            'color': '#8B4513',
            'subcategories': {
                'Grain': ['Bread', 'Malt', 'Rice'],
                'Burnt': ['Smoky', 'Ashy', 'Acrid']
            }
        }
    }
    
    # Create concentric circles for the wheel
    ax.set_xlim(-3, 3)
    ax.set_ylim(-3, 3)
    ax.set_aspect('equal')
    
    # Draw the wheel
    total_categories = len(flavor_categories)
    angle_per_category = 360 / total_categories
    
    for i, (category, data) in enumerate(flavor_categories.items()):
        start_angle = i * angle_per_category
        end_angle = (i + 1) * angle_per_category
        
        # Main category wedge (outer ring)
        wedge = Wedge((0, 0), 2.5, start_angle, end_angle,
                     width=0.5, facecolor=data['color'], alpha=0.8,
                     edgecolor='white', linewidth=2)
        ax.add_patch(wedge)
        
        # Category label
        mid_angle = np.radians((start_angle + end_angle) / 2)
        label_x = 2.7 * np.cos(mid_angle)
        label_y = 2.7 * np.sin(mid_angle)
        ax.text(label_x, label_y, category, ha='center', va='center',
               fontsize=12, fontweight='bold', rotation=0)
        
        # Subcategories (inner rings)
        subcats = list(data['subcategories'].keys())
        if subcats:
            subcat_angle = angle_per_category / len(subcats)
            for j, subcat in enumerate(subcats):
                sub_start = start_angle + j * subcat_angle
                sub_end = start_angle + (j + 1) * subcat_angle
                
                # Subcategory wedge
                sub_wedge = Wedge((0, 0), 2.0, sub_start, sub_end,
                                width=0.5, facecolor=data['color'], alpha=0.6,
                                edgecolor='white', linewidth=1)
                ax.add_patch(sub_wedge)
                
                # Check if any flavors from this subcategory are selected
                subcat_flavors = data['subcategories'][subcat]
                selected_in_subcat = [f for f in selected_flavors if f in subcat_flavors]
                
                if selected_in_subcat:
                    # Highlight selected subcategory
                    highlight_wedge = Wedge((0, 0), 2.0, sub_start, sub_end,
                                          width=0.5, facecolor='gold', alpha=0.9,
                                          edgecolor='red', linewidth=3)
                    ax.add_patch(highlight_wedge)
                    
                    # Add selected flavor text
                    sub_mid_angle = np.radians((sub_start + sub_end) / 2)
                    text_x = 1.3 * np.cos(sub_mid_angle)
                    text_y = 1.3 * np.sin(sub_mid_angle)
                    ax.text(text_x, text_y, '✓', ha='center', va='center',
                           fontsize=16, fontweight='bold', color='red')
    
    # Center circle
    center_circle = plt.Circle((0, 0), 1.0, facecolor='white', edgecolor='#8B4513', linewidth=3)
    ax.add_patch(center_circle)
    
    # Title in center
    ax.text(0, 0.2, 'SCA', ha='center', va='center', fontsize=16, fontweight='bold', color='#8B4513')
    ax.text(0, -0.2, 'Flavor Wheel', ha='center', va='center', fontsize=12, fontweight='bold', color='#8B4513')
    
    # Legend for selected flavors
    if selected_flavors:
        legend_text = "Selected Flavors:\n" + "\n".join([f"• {flavor}" for flavor in selected_flavors[:8]])
        ax.text(3.5, 2, legend_text, ha='left', va='top', fontsize=10,
               bbox=dict(boxstyle="round,pad=0.3", facecolor='lightyellow', alpha=0.8))
    
    ax.set_title('Coffee Flavor Profile', size=16, fontweight='bold', pad=20)
    ax.axis('off')
    
    # Save to temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png', dir=tempfile.gettempdir())
    plt.savefig(temp_file.name, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return temp_file.name

def generate_cupping_pdf(session):
    """Generate PDF report for cupping session"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        textColor=colors.HexColor('#8B4513'),
        alignment=1  # Center
    )
    
    story.append(Paragraph(f"☕ Coffee Cupping Report", title_style))
    story.append(Paragraph(f"Session: {session['name']}", styles['Heading2']))
    story.append(Spacer(1, 12))
    
    # Session Info
    session_data = [
        ['Date:', session['date']],
        ['Lead Cupper:', session['cupper']],
        ['Protocol:', session['protocol']],
        ['Water Temperature:', f"{session['water_temp']}°C"],
        ['Samples:', str(len(session['samples']))],
        ['Cups per Sample:', str(session['cups_per_sample'])],
        ['Blind Cupping:', 'Yes' if session['blind'] else 'No'],
        ['Status:', session['status']]
    ]
    
    session_table = Table(session_data, colWidths=[2*inch, 3*inch])
    session_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F5F5DC')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#D2B48C')),
    ]))
    
    story.append(session_table)
    story.append(Spacer(1, 20))
    
    # Samples Information
    story.append(Paragraph("Sample Information", styles['Heading2']))
    story.append(Spacer(1, 12))
    
    for i, sample in enumerate(session['samples']):
        sample_data = [
            [f"Sample {i+1}", sample['name']],
            ['Origin:', sample['origin']],
            ['Variety:', sample['variety']],
            ['Process:', sample['process']],
            ['Altitude:', sample['altitude']],
            ['Harvest Year:', sample['harvest_year']]
        ]
        
        sample_table = Table(sample_data, colWidths=[1.5*inch, 3.5*inch])
        sample_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F0F8FF')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(sample_table)
        story.append(Spacer(1, 10))
    
    # Scores (if available)
    if session.get('status') == 'Scored' and 'scores' in session:
        story.append(Paragraph("Cupping Scores & Visual Analysis", styles['Heading2']))
        story.append(Spacer(1, 12))
        
        # Create and add score visualization
        try:
            score_chart_path = create_score_visualization(session['scores'])
            score_img = Image(score_chart_path, width=7*inch, height=3.5*inch)
            story.append(score_img)
            story.append(Spacer(1, 15))
            
            # Clean up temp file
            os.unlink(score_chart_path)
        except Exception as e:
            story.append(Paragraph(f"Score visualization unavailable: {str(e)}", styles['Normal']))
            story.append(Spacer(1, 10))
        
        # Scores table header
        score_data = [['Sample', 'Fragrance', 'Flavor', 'Aftertaste', 'Acidity', 'Body', 'Balance', 'Overall', 'Total']]
        
        for score in session['scores']:
            score_data.append([
                score['sample_name'],
                str(score['fragrance']),
                str(score['flavor']),
                str(score['aftertaste']),
                str(score['acidity']),
                str(score['body']),
                str(score['balance']),
                str(score['overall']),
                f"{score['total']:.2f}"
            ])
        
        scores_table = Table(score_data, colWidths=[1.2*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.7*inch, 0.8*inch])
        scores_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8B4513')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F5F5DC')),
        ]))
        
        story.append(scores_table)
        story.append(Spacer(1, 20))
        
        # Flavor notes
        story.append(Paragraph("Tasting Notes & Flavor Profile", styles['Heading2']))
        story.append(Spacer(1, 12))
        
        # Collect all selected flavors from all samples
        all_selected_flavors = []
        for score in session['scores']:
            if score.get('selected_flavors'):
                all_selected_flavors.extend(score['selected_flavors'])
            if score.get('notes'):
                story.append(Paragraph(f"<b>{score['sample_name']}:</b> {score['notes']}", styles['Normal']))
                story.append(Spacer(1, 8))
        
        # Remove duplicates and create flavor wheel
        unique_flavors = list(set(all_selected_flavors))
        if unique_flavors:
            try:
                flavor_wheel_path = create_flavor_wheel(unique_flavors)
                flavor_img = Image(flavor_wheel_path, width=6*inch, height=6*inch)
                story.append(Spacer(1, 15))
                story.append(flavor_img)
                story.append(Spacer(1, 10))
                
                # Clean up temp file
                os.unlink(flavor_wheel_path)
            except Exception as e:
                story.append(Paragraph(f"Flavor wheel unavailable: {str(e)}", styles['Normal']))
                story.append(Spacer(1, 10))
        
        # Session notes
        if session.get('session_notes'):
            story.append(Spacer(1, 12))
            story.append(Paragraph("Session Notes", styles['Heading3']))
            story.append(Paragraph(session['session_notes'], styles['Normal']))
    
    # Footer
    story.append(Spacer(1, 30))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=1
    )
    story.append(Paragraph("Generated by Coffee Cupping App - Professional | © 2025 Rodrigo Bermudez - Cafe Cultura LLC", footer_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

def generate_participant_invite_pdf(session, participant_email):
    """Generate invitation PDF for cupping participants"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        spaceAfter=30,
        textColor=colors.HexColor('#8B4513'),
        alignment=1
    )
    
    story.append(Paragraph("☕ Coffee Cupping Invitation", title_style))
    story.append(Spacer(1, 20))
    
    # Invitation text
    invite_text = f"""
    <para align=center>
    <b>You are cordially invited to participate in a professional coffee cupping session!</b>
    </para>
    """
    story.append(Paragraph(invite_text, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Session details
    session_info = [
        ['Session Name:', session['name']],
        ['Date:', session['date']],
        ['Lead Cupper:', session['cupper']],
        ['Protocol:', session['protocol']],
        ['Number of Samples:', str(len(session['samples']))],
        ['Cups per Sample:', str(session['cups_per_sample'])],
        ['Blind Cupping:', 'Yes' if session['blind'] else 'No']
    ]
    
    info_table = Table(session_info, colWidths=[2*inch, 3*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#D2B48C')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    story.append(info_table)
    story.append(Spacer(1, 30))
    
    # Instructions
    instructions = """
    <b>What to Expect:</b><br/>
    • Professional SCA cupping protocol<br/>
    • Evaluation of multiple coffee samples<br/>
    • Flavor profiling and scoring<br/>
    • Collaborative tasting experience<br/><br/>
    
    <b>Please bring:</b><br/>
    • A clean palate<br/>
    • Water for rinsing<br/>
    • Note-taking materials<br/>
    • An open mind for discovery!<br/><br/>
    
    We look forward to your participation in this exciting coffee evaluation session.
    """
    
    story.append(Paragraph(instructions, styles['Normal']))
    story.append(Spacer(1, 30))
    
    # Contact info
    contact_style = ParagraphStyle(
        'Contact',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#8B4513'),
        alignment=1
    )
    
    story.append(Paragraph(f"For questions, contact: {session['cupper']}", contact_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Generated by Coffee Cupping App - Professional", contact_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

def get_text(key):
    translations = {
        'en': {
            'app_title': 'Professional Coffee Cupping App',
            'app_subtitle': 'Professional Protocol Implementation',
            'login': 'Login',
            'register': 'Register',
            'guest': 'Guest',
            'logout': 'Logout',
            'dashboard': 'Dashboard',
            'cupping_sessions': 'Cupping Sessions',
            'coffee_reviews': 'Coffee Reviews',
            'profile': 'Profile',
            'my_cupping_sessions': 'My Cupping Sessions',
            'new_session': 'New Session',
            'my_sessions': 'My Sessions',
            'analysis': 'Analysis',
            'flavor_wheel': 'Flavor Wheel',
            'score_session': 'Score Session',
            'view_samples': 'View Samples',
            'view_results': 'View Results',
            'delete': 'Delete',
            'completed': 'Completed',
            'welcome': 'Welcome',
            'protocol': 'Protocol',
            'water_temperature': 'Water Temperature',
            'samples': 'Samples',
            'sample': 'Sample',
            'cups_per_sample': 'Cups per Sample',
            'cup': 'Cup',
            'cups': 'Cups',
            'blind_cupping': 'Blind Cupping',
            'yes': 'Yes',
            'no': 'No',
            'created': 'Created'
        },
        'es': {
            'app_title': 'App Profesional de Cata de Café',
            'app_subtitle': 'Implementación Protocolo Profesional',
            'login': 'Iniciar Sesión',
            'register': 'Registrarse',
            'guest': 'Invitado',
            'logout': 'Cerrar Sesión',
            'dashboard': 'Panel Principal',
            'cupping_sessions': 'Sesiones de Cata',
            'coffee_reviews': 'Reseñas de Café',
            'profile': 'Perfil',
            'my_cupping_sessions': 'Mis Sesiones de Cata',
            'new_session': 'Nueva Sesión',
            'my_sessions': 'Mis Sesiones',
            'analysis': 'Análisis',
            'flavor_wheel': 'Rueda de Sabores',
            'score_session': 'Calificar Sesión',
            'view_samples': 'Ver Muestras',
            'view_results': 'Ver Resultados',
            'delete': 'Eliminar',
            'completed': 'Completado',
            'welcome': 'Bienvenido',
            'protocol': 'Protocolo',
            'water_temperature': 'Temperatura del Agua',
            'samples': 'Muestras',
            'sample': 'Muestra',
            'cups_per_sample': 'Tazas por Muestra',
            'cup': 'Taza',
            'cups': 'Tazas',
            'blind_cupping': 'Cata Ciega',
            'yes': 'Sí',
            'no': 'No',
            'created': 'Creado'
        }
    }
    return translations.get(get_language(), {}).get(key, key)

def main():
    # Initialize data on app start
    init_data()
    
    # Language selector
    col1, col2 = st.columns([4, 1])
    with col2:
        language_options = {"🇺🇸 English": "en", "🇪🇸 Español": "es"}
        selected_lang = st.selectbox(
            "🌐",
            options=list(language_options.keys()),
            index=0 if get_language() == 'en' else 1,
            key="language_selector"
        )
        if language_options[selected_lang] != get_language():
            st.session_state.language = language_options[selected_lang]
            st.rerun()
    
    # Header
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #8B4513, #D2B48C); padding: 2rem; border-radius: 15px; text-align: center; margin-bottom: 2rem;">
        <h1 style="color: white; margin: 0; font-size: 3rem;">☕ {get_text("app_title")}</h1>
        <p style="color: #F5F5DC; margin: 0; font-size: 1.2rem;">Professional Coffee Cupping Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Authentication
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        show_login()
    else:
        show_main_app()
    
    # Footer
    st.markdown("---")
    st.markdown("© 2025 Rodrigo Bermudez - Cafe Cultura LLC. All rights reserved.", 
                unsafe_allow_html=True)

def show_login():
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="coffee-card">', unsafe_allow_html=True)
        
        tab1, tab2, tab3 = st.tabs([f"🔐 {get_text('login')}", f"🆕 {get_text('register')}", f"👥 {get_text('guest')}"])
        
        with tab1:
            show_login_form()
        
        with tab2:
            show_register_form()
        
        with tab3:
            show_guest_mode()
        
        st.markdown('</div>', unsafe_allow_html=True)

def show_main_app():
    user_data = st.session_state.get('user_data', {})
    
    # Header with user info
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        st.markdown(f"## 👋 {get_text('welcome')}, {user_data.get('name', 'User')}!")
        
    with col2:
        st.markdown(f"📧 **{user_data.get('email', '')}**")
        st.markdown(f"🏢 **{user_data.get('company', '')}**")
    
    with col3:
        if st.button(get_text("logout")):
            st.session_state.logged_in = False
            st.rerun()
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("### ☕ Navigation")
        page = st.radio("", [
            f"📊 {get_text('dashboard')}", 
            f"☕ {get_text('cupping_sessions')}", 
            f"📝 {get_text('coffee_reviews')}",
            f"🏪 Coffee Shops", 
            f"👤 {get_text('profile')}"
        ])
    
    # Main content
    if page.endswith(get_text('dashboard')):
        show_dashboard()
    elif page.endswith(get_text('cupping_sessions')):
        show_cupping_sessions()
    elif page.endswith(get_text('coffee_reviews')):
        show_coffee_reviews()
    elif page.endswith("Coffee Shops"):
        show_coffee_shops()
    elif page.endswith(get_text('profile')):
        show_profile()

def show_dashboard():
    st.title(f"📊 {get_text('dashboard')}")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Reviews", "8", "2")
    with col2:
        st.metric("Average Rating", "4.2", "0.3")
    with col3:
        st.metric("Coffee Origins", "5", "1")
    with col4:
        st.metric("This Month", "3", "1")
    
    st.markdown("---")
    st.subheader("Recent Activity")
    st.success("✅ Welcome to your coffee cupping dashboard!")

def show_coffee_shops():
    st.title("🏪 Coffee Shop Reviews")
    
    tab1, tab2, tab3 = st.tabs(["🆕 New Review", "📋 My Reviews", "📊 Analysis"])
    
    with tab1:
        st.subheader("🆕 Review Coffee Shop")
        
        with st.form("coffee_shop_review"):
            col1, col2 = st.columns(2)
            
            with col1:
                shop_name = st.text_input("Coffee Shop Name *")
                location = st.text_input("Location/Address")
                city = st.text_input("City *")
                visit_date = st.date_input("Visit Date", value=date.today())
                
            with col2:
                shop_type = st.selectbox("Shop Type", [
                    "", "Specialty Coffee", "Chain Store", "Local Café", 
                    "Roastery Café", "Third Wave", "Traditional Café"
                ])
                atmosphere = st.selectbox("Atmosphere", [
                    "", "Cozy", "Modern", "Industrial", "Vintage", 
                    "Minimalist", "Bustling", "Quiet"
                ])
                wifi = st.checkbox("WiFi Available")
                laptop_friendly = st.checkbox("Laptop Friendly")
            
            # Coffee evaluation
            st.markdown("### ☕ Coffee Quality")
            col1, col2 = st.columns(2)
            
            with col1:
                coffee_ordered = st.text_input("Coffee Ordered")
                brewing_method = st.selectbox("Brewing Method", [
                    "", "Espresso", "Pour Over", "French Press", "Aeropress", 
                    "Cold Brew", "Drip Coffee", "Other"
                ])
                coffee_rating = st.select_slider("Coffee Quality", 
                                               options=[1,2,3,4,5], 
                                               value=3,
                                               format_func=lambda x: "⭐" * x)
            
            with col2:
                beans_origin = st.text_input("Bean Origin (if known)")
                roast_level = st.selectbox("Roast Level", ["", "Light", "Medium", "Dark", "Unknown"])
                price_coffee = st.number_input("Coffee Price ($)", min_value=0.0, step=0.25, format="%.2f")
            
            # Service and experience
            st.markdown("### 🛎️ Service & Experience")
            col1, col2 = st.columns(2)
            
            with col1:
                service_rating = st.select_slider("Service Quality", 
                                                options=[1,2,3,4,5], 
                                                value=3,
                                                format_func=lambda x: "⭐" * x)
                atmosphere_rating = st.select_slider("Atmosphere", 
                                                   options=[1,2,3,4,5], 
                                                   value=3,
                                                   format_func=lambda x: "⭐" * x)
            
            with col2:
                value_rating = st.select_slider("Value for Money", 
                                              options=[1,2,3,4,5], 
                                              value=3,
                                              format_func=lambda x: "⭐" * x)
                cleanliness_rating = st.select_slider("Cleanliness", 
                                                    options=[1,2,3,4,5], 
                                                    value=3,
                                                    format_func=lambda x: "⭐" * x)
            
            # Additional details
            st.markdown("### 📝 Additional Details")
            food_available = st.checkbox("Food Available")
            if food_available:
                food_quality = st.select_slider("Food Quality", 
                                               options=[1,2,3,4,5], 
                                               value=3,
                                               format_func=lambda x: "⭐" * x)
            else:
                food_quality = 0
            
            seating_comfort = st.selectbox("Seating Comfort", [
                "", "Very Comfortable", "Comfortable", "Average", "Uncomfortable"
            ])
            
            noise_level = st.selectbox("Noise Level", [
                "", "Very Quiet", "Quiet", "Moderate", "Loud", "Very Loud"
            ])
            
            # Overall review
            st.markdown("### 🌟 Overall Review")
            overall_rating = st.select_slider("Overall Experience", 
                                            options=[1,2,3,4,5], 
                                            value=3,
                                            format_func=lambda x: "⭐" * x)
            
            highlights = st.text_area("Highlights", placeholder="What did you love about this place?")
            improvements = st.text_area("Areas for Improvement", placeholder="What could be better?")
            notes = st.text_area("Additional Notes", placeholder="Any other observations...")
            
            would_return = st.radio("Would you return?", ["Definitely", "Probably", "Maybe", "Probably Not", "Never"])
            would_recommend = st.radio("Would you recommend?", ["Highly Recommend", "Recommend", "Neutral", "Not Recommend"])
            
            submit = st.form_submit_button("💾 Save Coffee Shop Review", use_container_width=True)
            
            if submit:
                if not shop_name:
                    st.error("❌ Coffee shop name is required")
                elif not city:
                    st.error("❌ City is required")
                else:
                    # Ensure coffee_shops exists and is a list
                    if 'coffee_shops' not in st.session_state:
                        st.session_state.coffee_shops = []
                    elif not isinstance(st.session_state.coffee_shops, list):
                        st.session_state.coffee_shops = []
                    
                    # Calculate overall score
                    scores = [coffee_rating, service_rating, atmosphere_rating, value_rating, cleanliness_rating]
                    if food_available and food_quality > 0:
                        scores.append(food_quality)
                    
                    avg_score = sum(scores) / len(scores)
                    
                    review = {
                        'shop_name': shop_name,
                        'location': location,
                        'city': city,
                        'visit_date': visit_date.strftime('%Y-%m-%d'),
                        'shop_type': shop_type or "Unknown",
                        'atmosphere': atmosphere or "Unknown",
                        'wifi': wifi,
                        'laptop_friendly': laptop_friendly,
                        'coffee_ordered': coffee_ordered,
                        'brewing_method': brewing_method or "Unknown",
                        'coffee_rating': coffee_rating,
                        'beans_origin': beans_origin,
                        'roast_level': roast_level or "Unknown",
                        'price_coffee': price_coffee,
                        'service_rating': service_rating,
                        'atmosphere_rating': atmosphere_rating,
                        'value_rating': value_rating,
                        'cleanliness_rating': cleanliness_rating,
                        'food_available': food_available,
                        'food_quality': food_quality,
                        'seating_comfort': seating_comfort or "Unknown",
                        'noise_level': noise_level or "Unknown",
                        'overall_rating': overall_rating,
                        'avg_score': avg_score,
                        'highlights': highlights,
                        'improvements': improvements,
                        'notes': notes,
                        'would_return': would_return,
                        'would_recommend': would_recommend,
                        'reviewer': st.session_state.get('user_data', {}).get('name', 'User'),
                        'review_date': datetime.now().strftime('%Y-%m-%d %H:%M')
                    }
                    
                    try:
                        st.session_state.coffee_shops.append(review)
                        # Auto-save after creating review
                        save_data()
                        st.success("✅ Coffee shop review saved successfully!")
                        st.balloons()
                    except Exception as e:
                        st.error(f"Error saving review: {e}")
                        st.session_state.coffee_shops = []  # Reset if corrupted
    
    with tab2:
        st.subheader("📋 My Coffee Shop Reviews")
        
        if 'coffee_shops' in st.session_state and st.session_state.coffee_shops:
            # Sort by visit date (newest first)
            sorted_reviews = sorted(st.session_state.coffee_shops, 
                                  key=lambda x: x['visit_date'], reverse=True)
            
            for review in sorted_reviews:
                # Overall rating color
                if review['overall_rating'] >= 4:
                    rating_color = "#28a745"
                elif review['overall_rating'] >= 3:
                    rating_color = "#ffc107" 
                else:
                    rating_color = "#dc3545"
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"### 🏪 {review['shop_name']}")
                    st.markdown(f"📍 **{review['city']}** | 📅 **{review['visit_date']}** | ☕ **{review['coffee_ordered']}**")
                
                with col2:
                    st.markdown(f"""
                    <div style="background: {rating_color}; color: white; padding: 0.5rem; border-radius: 10px; text-align: center;">
                        <h3 style="margin: 0;">{"⭐" * review['overall_rating']}</h3>
                        <p style="margin: 0; font-size: 0.8rem;">Overall</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Details in columns
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f"""
                    **☕ Coffee:** {"⭐" * review['coffee_rating']}  
                    **🛎️ Service:** {"⭐" * review['service_rating']}  
                    **💰 Value:** {"⭐" * review['value_rating']}
                    """)
                
                with col2:
                    st.markdown(f"""
                    **🏛️ Atmosphere:** {"⭐" * review['atmosphere_rating']}  
                    **🧽 Cleanliness:** {"⭐" * review['cleanliness_rating']}  
                    **💻 WiFi:** {"✅" if review['wifi'] else "❌"}
                    """)
                
                with col3:
                    st.markdown(f"""
                    **🔄 Return:** {review['would_return']}  
                    **👍 Recommend:** {review['would_recommend']}  
                    **💵 Price:** ${review['price_coffee']:.2f}
                    """)
                
                if review['highlights']:
                    st.markdown(f"**✨ Highlights:** {review['highlights']}")
                
                if review['improvements']:
                    st.markdown(f"**📈 Improvements:** {review['improvements']}")
                
                st.markdown("---")
        else:
            st.info("🏪 No coffee shop reviews yet. Visit your first coffee shop and share your experience!")
    
    with tab3:
        st.subheader("📊 Coffee Shop Analysis")
        
        if 'coffee_shops' in st.session_state and st.session_state.coffee_shops:
            reviews = st.session_state.coffee_shops
            
            # Overview metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Visits", len(reviews))
            with col2:
                avg_overall = sum(r['overall_rating'] for r in reviews) / len(reviews)
                st.metric("Avg Overall Rating", f"{avg_overall:.1f}⭐")
            with col3:
                unique_cities = len(set(r['city'] for r in reviews))
                st.metric("Cities Visited", unique_cities)
            with col4:
                total_spent = sum(r['price_coffee'] for r in reviews)
                st.metric("Total Coffee Spent", f"${total_spent:.2f}")
            
            st.markdown("---")
            
            # Top rated shops
            st.markdown("### 🏆 Top Rated Coffee Shops")
            top_shops = sorted(reviews, key=lambda x: x['overall_rating'], reverse=True)[:5]
            
            for shop in top_shops:
                st.markdown(f"""
                **{shop['shop_name']}** - {"⭐" * shop['overall_rating']}  
                📍 {shop['city']} | ☕ {shop['coffee_ordered']} | 💰 ${shop['price_coffee']:.2f}  
                *{shop['highlights'][:100]}{"..." if len(shop['highlights']) > 100 else ""}*
                """)
                st.markdown("---")
            
            # City analysis
            st.markdown("### 🌆 Performance by City")
            city_stats = {}
            for review in reviews:
                city = review['city']
                if city not in city_stats:
                    city_stats[city] = {'count': 0, 'ratings': [], 'cost': 0}
                city_stats[city]['count'] += 1
                city_stats[city]['ratings'].append(review['overall_rating'])
                city_stats[city]['cost'] += review['price_coffee']
            
            city_data = []
            for city, stats in city_stats.items():
                avg_rating = sum(stats['ratings']) / len(stats['ratings'])
                avg_cost = stats['cost'] / stats['count']
                city_data.append({
                    'City': city,
                    'Visits': stats['count'],
                    'Avg Rating': f"{avg_rating:.1f}⭐",
                    'Avg Cost': f"${avg_cost:.2f}",
                    'Total Spent': f"${stats['cost']:.2f}"
                })
            
            city_data.sort(key=lambda x: float(x['Avg Rating'].replace('⭐', '')), reverse=True)
            st.table(city_data)
            
        else:
            st.info("📊 No coffee shop data yet. Visit coffee shops to see analysis.")

def show_coffee_reviews():
    st.title("📝 Coffee Bag Evaluation")
    
    tab1, tab2 = st.tabs(["🆕 New Review", "📋 My Reviews"])
    
    with tab1:
        st.subheader("🆕 Evaluate Coffee")
        
        with st.form("coffee_evaluation"):
            col1, col2 = st.columns(2)
            
            with col1:
                coffee_name = st.text_input("Coffee Name *")
                producer = st.text_input("Producer/Roaster")
                origin = st.selectbox("Origin *", [
                    "", "Ethiopia", "Colombia", "Brazil", "Guatemala", "Kenya", 
                    "Costa Rica", "Jamaica", "Panama", "Honduras", "Other"
                ])
                cost = st.number_input("Cost (USD)", min_value=0.0, step=0.50, format="%.2f")
            
            with col2:
                roast_date = st.date_input("Roast Date")
                roast_level = st.selectbox("Roast Level", ["", "Light", "Medium", "Dark"])
                coffee_form = st.radio("Coffee Form", ["Whole Bean", "Pre-Ground"])
                preparation = st.selectbox("Preparation Method *", [
                    "", "Pour Over", "French Press", "Espresso", "Aeropress", "Other"
                ])
            
            # Sensory evaluation
            st.markdown("### 👃 Sensory Evaluation")
            col1, col2 = st.columns(2)
            
            with col1:
                dry_aroma = st.text_area("Dry Aroma (beans/grounds)", height=80)
                wet_aroma = st.text_area("Wet Aroma (brewed)", height=80)
            
            with col2:
                flavor_notes = st.text_area("Flavor Notes", height=160)
            
            # Rating and recommendations
            st.markdown("### ⭐ Rating & Recommendations")
            col1, col2 = st.columns(2)
            
            with col1:
                rating = st.select_slider("Overall Rating", 
                                        options=[1,2,3,4,5], 
                                        value=3,
                                        format_func=lambda x: "⭐" * x)
                recommend = st.radio("Would you recommend?", ["Yes", "Maybe", "No"])
            
            with col2:
                buy_again = st.radio("Would you buy again?", ["Yes", "Maybe", "No"])
                grind_size = "N/A"
                if coffee_form == "Pre-Ground":
                    grind_size = st.selectbox("Grind Size", [
                        "Extra Coarse", "Coarse", "Medium", "Fine", "Extra Fine"
                    ])
            
            submit = st.form_submit_button("📝 Save Coffee Review", use_container_width=True)
            
            if submit:
                if not coffee_name:
                    st.error("❌ Coffee name is required")
                elif not origin:
                    st.error("❌ Origin is required")
                elif not preparation:
                    st.error("❌ Preparation method is required")
                else:
                    # Ensure coffee_reviews exists and is a list
                    if 'coffee_reviews' not in st.session_state:
                        st.session_state.coffee_reviews = []
                    elif not isinstance(st.session_state.coffee_reviews, list):
                        st.session_state.coffee_reviews = []
                    
                    review = {
                        'name': coffee_name,
                        'producer': producer or "Unknown",
                        'origin': origin,
                        'cost': cost,
                        'roast_date': roast_date.strftime('%Y-%m-%d'),
                        'roast_level': roast_level or "Unknown",
                        'form': coffee_form,
                        'grind_size': grind_size,
                        'preparation': preparation,
                        'dry_aroma': dry_aroma,
                        'wet_aroma': wet_aroma,
                        'flavor_notes': flavor_notes,
                        'rating': rating,
                        'recommend': recommend,
                        'buy_again': buy_again,
                        'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
                        'reviewer': user_data.get('name', 'User')
                    }
                    
                    try:
                        st.session_state.coffee_reviews.append(review)
                        # Auto-save after creating review
                        save_data()
                        st.success("✅ Coffee review saved successfully!")
                        st.balloons()
                    except Exception as e:
                        st.error(f"Error saving review: {e}")
                        st.session_state.coffee_reviews = []  # Reset if corrupted
    
    with tab2:
        st.subheader("📋 My Coffee Reviews")
        
        if 'coffee_reviews' in st.session_state and st.session_state.coffee_reviews:
            for review in st.session_state.coffee_reviews:
                st.markdown(f'''
                <div class="coffee-card">
                    <h4>☕ {review["name"]}</h4>
                    <p><strong>🌍 Origin:</strong> {review["origin"]} | <strong>🏷️ Producer:</strong> {review["producer"]}</p>
                    <p><strong>⭐ Rating:</strong> {"⭐" * review["rating"]} | <strong>💰 Cost:</strong> ${review["cost"]:.2f}</p>
                    <p><strong>🔥 Roast:</strong> {review["roast_level"]} | <strong>☕ Method:</strong> {review["preparation"]}</p>
                    <p><strong>🎨 Flavors:</strong> <em>"{review["flavor_notes"]}"</em></p>
                    <p><strong>👍 Recommend:</strong> {review["recommend"]} | <strong>🔄 Buy Again:</strong> {review["buy_again"]}</p>
                    <p style="font-size: 0.9rem; color: #666;"><strong>📅 Reviewed:</strong> {review["date"]}</p>
                </div>
                ''', unsafe_allow_html=True)
        else:
            st.info("📝 No reviews yet. Create your first coffee evaluation!")

def show_profile():
    st.title("👤 Profile")
    
    user_data = st.session_state.get('user_data', {})
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Profile Information")
        st.text_input("Name", value=user_data.get('name', ''))
        st.text_input("Email", value=user_data.get('email', ''), disabled=True)
        st.text_input("Company", value=user_data.get('company', ''))
    
    with col2:
        st.subheader("Statistics")
        reviews_count = len(st.session_state.get('coffee_reviews', []))
        st.metric("Total Reviews", reviews_count)
        if reviews_count > 0:
            avg_rating = sum(r['rating'] for r in st.session_state.coffee_reviews) / reviews_count
            st.metric("Average Rating", f"{avg_rating:.1f}⭐")

def show_cupping_sessions():
    st.title("☕ Professional Cupping Sessions")
    
    tab1, tab2, tab3, tab4 = st.tabs(["🆕 New Session", "📋 My Sessions", "📊 Analysis", "☕ Coffee Bags"])
    
    with tab1:
        show_new_cupping_session()
    
    with tab2:
        show_my_cupping_sessions()
    
    with tab3:
        show_cupping_analysis()
    
    with tab4:
        show_coffee_bags_analysis()

def show_new_cupping_session():
    st.subheader("🆕 Create New Cupping Session")
    
    with st.form("new_cupping_session"):
        # Session details
        st.markdown("### 📋 Session Information")
        col1, col2 = st.columns(2)
        
        with col1:
            session_name = st.text_input("Session Name *")
            cupping_date = st.date_input("Cupping Date", value=date.today())
            num_samples = st.number_input("Number of Samples", 1, 8, 3)
            cups_per_sample = st.number_input("Cups per Sample", 3, 5, 5)
        
        with col2:
            cupper_name = st.text_input("Lead Cupper", value=st.session_state.get('user_data', {}).get('name', ''))
            evaluation_type = st.selectbox("Protocol", ["SCA Standard", "COE Protocol", "Custom"])
            is_blind = st.checkbox("Blind Cupping", value=True)
            water_temp = st.number_input("Water Temperature (°C)", 90, 96, 93)
        
        # Sample information
        st.markdown("### 🌱 Sample Information")
        samples = []
        
        for i in range(num_samples):
            st.markdown(f"**Sample {i+1}:**")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                sample_name = st.text_input(f"Sample Name", key=f"sample_name_{i}")
                origin = st.text_input(f"Origin", key=f"origin_{i}")
            
            with col2:
                variety = st.text_input(f"Variety", key=f"variety_{i}")
                process = st.selectbox(f"Process", ["Washed", "Natural", "Honey", "Pulped Natural"], key=f"process_{i}")
            
            with col3:
                altitude = st.text_input(f"Altitude (masl)", key=f"altitude_{i}")
                harvest_year = st.text_input(f"Harvest Year", key=f"harvest_{i}")
            
            samples.append({
                'name': sample_name,
                'origin': origin,
                'variety': variety,
                'process': process,
                'altitude': altitude,
                'harvest_year': harvest_year
            })
            
            if i < num_samples - 1:
                st.markdown("---")
        
        submit = st.form_submit_button("🚀 Create Cupping Session", use_container_width=True)
        
        if submit:
            if not session_name:
                st.error("❌ Session name is required")
            else:
                # Ensure cupping_sessions exists and is a list
                if 'cupping_sessions' not in st.session_state:
                    st.session_state.cupping_sessions = []
                elif not isinstance(st.session_state.cupping_sessions, list):
                    st.session_state.cupping_sessions = []
                
                session = {
                    'name': session_name,
                    'date': cupping_date.strftime('%Y-%m-%d'),
                    'cupper': cupper_name,
                    'protocol': evaluation_type,
                    'blind': is_blind,
                    'water_temp': water_temp,
                    'samples': samples,
                    'cups_per_sample': cups_per_sample,
                    'created': datetime.now().strftime('%Y-%m-%d %H:%M'),
                    'status': 'Created'
                }
                
                try:
                    st.session_state.cupping_sessions.append(session)
                    # Auto-save after creating session
                    save_data()
                    st.success(f"✅ Created cupping session: '{session_name}' with {num_samples} samples")
                    st.balloons()
                except Exception as e:
                    st.error(f"Error creating session: {e}")
                    st.session_state.cupping_sessions = []  # Reset if corrupted

def show_my_cupping_sessions():
    st.subheader(f"📋 {get_text('my_cupping_sessions')}")
    
    if 'cupping_sessions' in st.session_state and st.session_state.cupping_sessions:
        for i, session in enumerate(st.session_state.cupping_sessions):
            # Status color coding
            if session["status"] == "Scored":
                status_color = "#28a745"
                status_icon = "✅"
            else:
                status_color = "#ffc107"
                status_icon = "⏳"
            
            # Calculate average score if scored
            avg_score = ""
            if session["status"] == "Scored" and 'scores' in session:
                total_avg = sum(score['total'] for score in session['scores']) / len(session['scores'])
                avg_score = f"<span style='font-size: 1.5rem; color: {status_color}; font-weight: bold;'>⭐ {total_avg:.1f}</span>"
            
            # Session header
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"### ☕ {session['name']}")
                st.markdown(f"📅 **{session['date']}** | 👨‍🔬 **{session['cupper']}**")
            
            with col2:
                if session["status"] == "Scored":
                    st.success(f"✅ {session['status']}")
                    if 'scores' in session:
                        total_avg = sum(score['total'] for score in session['scores']) / len(session['scores'])
                        st.metric("Score", f"{total_avg:.1f}")
                else:
                    st.warning(f"⏳ {session['status']}")
            
            # Session details in clean format
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                **🔬 {get_text("protocol")}:** {session["protocol"]}  
                **🌡️ {get_text("water_temperature")}:** {session["water_temp"]}°C
                """)
            
            with col2:
                sample_count = len(session["samples"])
                sample_word = get_text("sample" if sample_count == 1 else "samples")
                cups_count = session["cups_per_sample"]
                cup_word = get_text("cup" if cups_count == 1 else "cups")
                st.markdown(f"""
                **🌱 {get_text("samples")}:** {sample_count} {sample_word}  
                **☕ {get_text("cups_per_sample")}:** {cups_count} {cup_word}
                """)
            
            with col3:
                blind_text = get_text("yes") if session["blind"] else get_text("no")
                st.markdown(f"""
                **👁️ {get_text("blind_cupping")}:** {blind_text}  
                **📅 {get_text("created")}:** {session["created"]}
                """)
            
            st.markdown("---")
            
            # Action buttons with better styling
            col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
            with col1:
                if session["status"] != "Scored":
                    if st.button(f"📊 {get_text('score_session')}", key=f"score_{i}", use_container_width=True):
                        st.session_state.scoring_session = i
                        st.rerun()
                else:
                    st.success(f"✅ {get_text('completed')}")
            
            with col2:
                if st.button(f"📋 {get_text('view_samples')}", key=f"view_{i}", use_container_width=True):
                    st.session_state.viewing_session = i
            
            with col3:
                if session["status"] == "Scored":
                    if st.button(f"📈 {get_text('view_results')}", key=f"results_{i}", use_container_width=True):
                        st.session_state.results_session = i
                else:
                    st.button(f"📈 {get_text('view_results')}", disabled=True, use_container_width=True)
            
            with col4:
                # PDF Export button
                try:
                    pdf_buffer = generate_cupping_pdf(session)
                    st.download_button(
                        label="📄 Export PDF",
                        data=pdf_buffer,
                        file_name=f"cupping_session_{session['name'].replace(' ', '_')}.pdf",
                        mime="application/pdf",
                        key=f"pdf_{i}",
                        use_container_width=True
                    )
                except Exception as e:
                    if st.button("📄 Export PDF", key=f"pdf_error_{i}", use_container_width=True):
                        st.error(f"PDF generation error: {e}")
            
            with col5:
                # Invite participants button
                if st.button("👥 Invite", key=f"invite_{i}", use_container_width=True):
                    st.session_state.inviting_session = i
            
            with col6:
                # Edit session button
                if st.button("✏️ Edit", key=f"edit_{i}", use_container_width=True):
                    st.session_state.editing_session = i
            
            with col7:
                if st.button(f"🗑️ {get_text('delete')}", key=f"delete_{i}", use_container_width=True):
                    if st.session_state.get(f'confirm_delete_{i}', False):
                        del st.session_state.cupping_sessions[i]
                        st.success("Session deleted")
                        st.rerun()
                    else:
                        st.session_state[f'confirm_delete_{i}'] = True
                        st.warning("Click again to confirm deletion")
        
        # Show scoring interface
        if 'scoring_session' in st.session_state:
            show_scoring_interface(st.session_state.scoring_session)
        
        # Show sample details
        if 'viewing_session' in st.session_state:
            session = st.session_state.cupping_sessions[st.session_state.viewing_session]
            with st.expander(f"📋 Sample Details - {session['name']}", expanded=True):
                for i, sample in enumerate(session['samples']):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**Sample {i+1}:** {sample['name']}")
                        st.write(f"**Origin:** {sample['origin']}")
                    with col2:
                        st.write(f"**Variety:** {sample['variety']}")
                        st.write(f"**Process:** {sample['process']}")
                    with col3:
                        st.write(f"**Altitude:** {sample['altitude']}")
                        st.write(f"**Harvest:** {sample['harvest_year']}")
                    if i < len(session['samples']) - 1:
                        st.markdown("---")
                if st.button("Close Details"):
                    del st.session_state.viewing_session
                    st.rerun()
        
        # Show invite interface
        if 'inviting_session' in st.session_state:
            show_invite_interface(st.session_state.inviting_session)
        
        # Show edit interface
        if 'editing_session' in st.session_state:
            show_edit_interface(st.session_state.editing_session)
        
        # Show results
        if 'results_session' in st.session_state:
            show_session_results(st.session_state.results_session)
            
    else:
        st.info("📝 No cupping sessions yet. Create your first professional cupping session!")

def show_cupping_analysis():
    st.subheader("📊 Professional Cupping Analysis")
    
    if 'cupping_sessions' in st.session_state and st.session_state.cupping_sessions:
        sessions_count = len(st.session_state.cupping_sessions)
        total_samples = sum(len(s['samples']) for s in st.session_state.cupping_sessions)
        scored_sessions = [s for s in st.session_state.cupping_sessions if s.get('status') == 'Scored']
        
        # Overview metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Sessions", sessions_count)
        with col2:
            st.metric("Total Samples", total_samples)
        with col3:
            st.metric("Scored Sessions", len(scored_sessions))
        with col4:
            completion_rate = (len(scored_sessions) / sessions_count * 100) if sessions_count > 0 else 0
            st.metric("Completion Rate", f"{completion_rate:.0f}%")
        
        st.markdown("---")
        
        # Score analysis for completed sessions
        if scored_sessions:
            st.markdown("### 🏆 Score Analysis")
            
            all_scores = []
            origin_scores = {}
            
            for session in scored_sessions:
                if 'scores' in session:
                    for score in session['scores']:
                        all_scores.append(score['total'])
                        
                        # Find sample origin from session samples
                        sample_name = score['sample_name']
                        for sample in session['samples']:
                            if sample['name'] == sample_name:
                                origin = sample.get('origin', 'Unknown')
                                if origin not in origin_scores:
                                    origin_scores[origin] = []
                                origin_scores[origin].append(score['total'])
                                break
            
            if all_scores:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Average Score", f"{sum(all_scores)/len(all_scores):.1f}")
                with col2:
                    st.metric("Highest Score", f"{max(all_scores):.1f}")
                with col3:
                    st.metric("Lowest Score", f"{min(all_scores):.1f}")
                
                # Score distribution
                st.markdown("### 📈 Score Distribution")
                excellent = len([s for s in all_scores if s >= 85])
                very_good = len([s for s in all_scores if 80 <= s < 85])
                good = len([s for s in all_scores if 75 <= s < 80])
                fair = len([s for s in all_scores if s < 75])
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("🏆 Excellent (85+)", excellent)
                with col2:
                    st.metric("⭐ Very Good (80-84)", very_good)
                with col3:
                    st.metric("👍 Good (75-79)", good)
                with col4:
                    st.metric("⚠️ Fair (<75)", fair)
                
                # Origin analysis
                if origin_scores:
                    st.markdown("### 🌍 Performance by Origin")
                    origin_data = []
                    for origin, scores in origin_scores.items():
                        if scores:
                            avg_score = sum(scores) / len(scores)
                            origin_data.append({
                                'Origin': origin,
                                'Samples': len(scores),
                                'Avg Score': f"{avg_score:.1f}",
                                'Best Score': f"{max(scores):.1f}"
                            })
                    
                    if origin_data:
                        # Sort by average score
                        origin_data.sort(key=lambda x: float(x['Avg Score']), reverse=True)
                        st.table(origin_data)
        
        st.markdown("---")
        st.markdown("### 📋 Session Overview")
        
        for session in st.session_state.cupping_sessions:
            status_icon = "✅" if session['status'] == 'Scored' else "⏳"
            score_info = ""
            if session['status'] == 'Scored' and 'scores' in session:
                avg = sum(score['total'] for score in session['scores']) / len(session['scores'])
                score_info = f" - Avg: {avg:.1f}"
            
            st.markdown(f"{status_icon} **{session['name']}** - {session['date']} - {len(session['samples'])} samples{score_info}")
    else:
        st.info("📊 No cupping data yet. Create sessions to see analysis.")

def show_coffee_bags_analysis():
    st.subheader("☕ Coffee Bag Analysis")
    
    if 'coffee_reviews' in st.session_state and st.session_state.coffee_reviews:
        reviews = st.session_state.coffee_reviews
        
        # Overview metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Reviews", len(reviews))
        with col2:
            avg_rating = sum(r['rating'] for r in reviews) / len(reviews)
            st.metric("Average Rating", f"{avg_rating:.1f}⭐")
        with col3:
            origins = len(set(r['origin'] for r in reviews))
            st.metric("Origins Tried", origins)
        with col4:
            total_cost = sum(r['cost'] for r in reviews)
            st.metric("Total Investment", f"${total_cost:.2f}")
        
        st.markdown("---")
        
        # Rating distribution
        st.markdown("### ⭐ Rating Distribution")
        rating_counts = {i: 0 for i in range(1, 6)}
        for review in reviews:
            rating_counts[review['rating']] += 1
        
        col1, col2, col3, col4, col5 = st.columns(5)
        cols = [col1, col2, col3, col4, col5]
        for i, (rating, count) in enumerate(rating_counts.items()):
            with cols[i]:
                st.metric(f"{rating}⭐", count)
        
        # Origin analysis
        st.markdown("### 🌍 Performance by Origin")
        origin_stats = {}
        for review in reviews:
            origin = review['origin']
            if origin not in origin_stats:
                origin_stats[origin] = {'count': 0, 'ratings': [], 'cost': 0}
            origin_stats[origin]['count'] += 1
            origin_stats[origin]['ratings'].append(review['rating'])
            origin_stats[origin]['cost'] += review['cost']
        
        origin_data = []
        for origin, stats in origin_stats.items():
            avg_rating = sum(stats['ratings']) / len(stats['ratings'])
            avg_cost = stats['cost'] / stats['count']
            origin_data.append({
                'Origin': origin,
                'Reviews': stats['count'],
                'Avg Rating': f"{avg_rating:.1f}⭐",
                'Avg Cost': f"${avg_cost:.2f}",
                'Total Spent': f"${stats['cost']:.2f}"
            })
        
        # Sort by average rating
        origin_data.sort(key=lambda x: float(x['Avg Rating'].replace('⭐', '')), reverse=True)
        st.table(origin_data)
        
        # Preparation method analysis
        st.markdown("### ☕ Preparation Method Analysis")
        prep_stats = {}
        for review in reviews:
            prep = review['preparation']
            if prep not in prep_stats:
                prep_stats[prep] = {'count': 0, 'ratings': []}
            prep_stats[prep]['count'] += 1
            prep_stats[prep]['ratings'].append(review['rating'])
        
        prep_data = []
        for prep, stats in prep_stats.items():
            avg_rating = sum(stats['ratings']) / len(stats['ratings'])
            prep_data.append({
                'Method': prep,
                'Reviews': stats['count'],
                'Avg Rating': f"{avg_rating:.1f}⭐"
            })
        
        prep_data.sort(key=lambda x: float(x['Avg Rating'].replace('⭐', '')), reverse=True)
        st.table(prep_data)
        
        # Top performers
        st.markdown("### 🏆 Top Rated Coffees")
        top_coffees = sorted(reviews, key=lambda x: x['rating'], reverse=True)[:5]
        
        for coffee in top_coffees:
            st.markdown(f"""
            **{coffee['name']}** - {"⭐" * coffee['rating']}  
            🌍 {coffee['origin']} | 💰 ${coffee['cost']:.2f} | ☕ {coffee['preparation']}  
            *"{coffee['flavor_notes']}"*
            """)
    else:
        st.info("☕ No coffee bag reviews yet. Create reviews in the Coffee Reviews section to see analysis.")


def show_scoring_interface(session_index):
    st.markdown("---")
    st.subheader("📊 SCA Cupping Score")
    
    session = st.session_state.cupping_sessions[session_index]
    st.markdown(f"### ☕ Scoring: {session['name']}")
    
    # Initialize if not exists
    if f'scoring_data_{session_index}' not in st.session_state:
        st.session_state[f'scoring_data_{session_index}'] = {}
    
    sample_scores = []
    
    for i, sample in enumerate(session['samples']):
        st.markdown(f"#### Sample {i+1}: {sample['name']} ({sample['origin']})")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            st.markdown("**🎯 SCA Categories**")
            # SCA Categories (6-10 scale) - NO FORM
            fragrance = st.slider(f"Fragrance/Aroma", 6.0, 10.0, 8.0, 0.25, key=f"fragrance_{session_index}_{i}")
            flavor = st.slider(f"Flavor", 6.0, 10.0, 8.0, 0.25, key=f"flavor_{session_index}_{i}")
            aftertaste = st.slider(f"Aftertaste", 6.0, 10.0, 8.0, 0.25, key=f"aftertaste_{session_index}_{i}")
            acidity = st.slider(f"Acidity", 6.0, 10.0, 8.0, 0.25, key=f"acidity_{session_index}_{i}")
            body = st.slider(f"Body", 6.0, 10.0, 8.0, 0.25, key=f"body_{session_index}_{i}")
        
        with col2:
            st.markdown("**⚖️ Quality Factors**")
            balance = st.slider(f"Balance", 6.0, 10.0, 8.0, 0.25, key=f"balance_{session_index}_{i}")
            uniformity = st.slider(f"Uniformity", 0, 10, 10, 2, key=f"uniformity_{session_index}_{i}")
            clean_cup = st.slider(f"Clean Cup", 0, 10, 10, 2, key=f"clean_{session_index}_{i}")
            sweetness = st.slider(f"Sweetness", 0, 10, 10, 2, key=f"sweetness_{session_index}_{i}")
            overall = st.slider(f"Overall", 6.0, 10.0, 8.0, 0.25, key=f"overall_{session_index}_{i}")
            
            # Defects
            defects = st.number_input(f"Defects (subtract)", 0, 10, 0, key=f"defects_{session_index}_{i}")
        
        with col3:
            st.markdown("**📊 Live Score**")
            # Calculate total DYNAMICALLY
            total = fragrance + flavor + aftertaste + acidity + body + balance + uniformity + clean_cup + sweetness + overall - defects
            
            # Show score with color coding
            if total >= 90:
                score_color = "#28a745"  # Green
                grade = "🏆 Outstanding"
            elif total >= 85:
                score_color = "#17a2b8"  # Blue
                grade = "⭐ Excellent"
            elif total >= 80:
                score_color = "#ffc107"  # Yellow
                grade = "👍 Very Good"
            elif total >= 75:
                score_color = "#fd7e14"  # Orange
                grade = "👌 Good"
            else:
                score_color = "#dc3545"  # Red
                grade = "⚠️ Fair"
            
            st.markdown(f'''
            <div style="background: {score_color}; color: white; padding: 1rem; border-radius: 10px; text-align: center; margin: 1rem 0;">
                <h2 style="margin: 0; font-size: 2rem;">{total:.2f}</h2>
                <p style="margin: 0; font-weight: bold;">{grade}</p>
            </div>
            ''', unsafe_allow_html=True)
            
            st.metric("vs Specialty (80)", f"{total-80:+.2f}", f"{((total-80)/80*100):+.1f}%")
        
        # Flavor Notes Section
        st.markdown("### 🎨 Flavor Profile")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Quick flavor buttons from SCA wheel
            st.markdown("**Quick Flavor Selection:**")
            
            # Flavor categories in compact form
            flavor_buttons = {
                "🍊 Fruity": ["Citrus", "Berry", "Stone Fruit", "Tropical"],
                "🌸 Floral": ["Rose", "Jasmine", "Tea-like"],
                "🍯 Sweet": ["Caramel", "Honey", "Chocolate", "Vanilla"],
                "🥜 Nutty": ["Almond", "Hazelnut", "Walnut"],
                "🌿 Green": ["Fresh", "Herb-like"],
                "🔥 Roasted": ["Bread", "Smoky", "Cereal"]
            }
            
            selected_flavors = []
            
            for category, flavors in flavor_buttons.items():
                st.markdown(f"**{category}:**")
                cols = st.columns(len(flavors))
                for j, flavor in enumerate(flavors):
                    with cols[j]:
                        if st.checkbox(flavor, key=f"flavor_{session_index}_{i}_{category}_{flavor}"):
                            selected_flavors.append(flavor)
            
            # Manual notes
            manual_notes = st.text_area(f"Additional Tasting Notes", key=f"notes_{session_index}_{i}", height=80,
                                      placeholder="e.g., bright, clean finish, wine-like...")
        
        with col2:
            st.markdown("**Selected Flavors:**")
            if selected_flavors:
                for flavor in selected_flavors:
                    st.markdown(f"🏷️ {flavor}")
                flavor_text = ", ".join(selected_flavors)
            else:
                flavor_text = ""
                st.info("Select flavors from categories")
            
            # Combine flavor notes
            combined_notes = f"{flavor_text}. {manual_notes}".strip('. ')
        
        sample_scores.append({
            'sample_name': sample['name'],
            'fragrance': fragrance,
            'flavor': flavor,
            'aftertaste': aftertaste,
            'acidity': acidity,
            'body': body,
            'balance': balance,
            'uniformity': uniformity,
            'clean_cup': clean_cup,
            'sweetness': sweetness,
            'overall': overall,
            'defects': defects,
            'total': total,
            'notes': combined_notes,
            'selected_flavors': selected_flavors
        })
        
        if i < len(session['samples']) - 1:
            st.markdown("---")
    
    # Session notes
    st.markdown("### 📝 Session Notes")
    session_notes = st.text_area("Overall session comments", key=f"session_notes_{session_index}")
    
    # Save/Cancel buttons (outside form for immediate updates)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 Save Scores", use_container_width=True, key=f"save_{session_index}"):
            # Save scores to session
            st.session_state.cupping_sessions[session_index]['scores'] = sample_scores
            st.session_state.cupping_sessions[session_index]['session_notes'] = session_notes
            st.session_state.cupping_sessions[session_index]['status'] = 'Scored'
            st.session_state.cupping_sessions[session_index]['scored_date'] = datetime.now().strftime('%Y-%m-%d %H:%M')
            
            st.success("✅ Scores saved successfully!")
            del st.session_state.scoring_session
            st.rerun()
    
    with col2:
        if st.button("❌ Cancel", use_container_width=True, key=f"cancel_{session_index}"):
            del st.session_state.scoring_session
            st.rerun()

def show_invite_interface(session_index):
    st.markdown("---")
    st.subheader("👥 Invite Cupping Participants")
    
    session = st.session_state.cupping_sessions[session_index]
    st.markdown(f"### ☕ Inviting to: {session['name']}")
    
    # Initialize participants list if not exists
    if 'participants' not in session:
        st.session_state.cupping_sessions[session_index]['participants'] = []
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### 📧 Add Participants")
        with st.form(f"invite_form_{session_index}"):
            participant_email = st.text_input("Participant Email", placeholder="cupper@coffee.com")
            participant_name = st.text_input("Participant Name", placeholder="Coffee Expert")
            participant_role = st.selectbox("Role", [
                "Q Grader", "Coffee Roaster", "Barista", "Coffee Buyer", 
                "Quality Control", "Coffee Farmer", "Coffee Enthusiast", "Other"
            ])
            
            col_a, col_b = st.columns(2)
            with col_a:
                add_participant = st.form_submit_button("➕ Add Participant", use_container_width=True)
            with col_b:
                send_invite = st.form_submit_button("📧 Generate Invite PDF", use_container_width=True)
            
            if add_participant:
                if participant_email and participant_name:
                    new_participant = {
                        'email': participant_email,
                        'name': participant_name,
                        'role': participant_role,
                        'invited_date': datetime.now().strftime('%Y-%m-%d %H:%M'),
                        'status': 'Invited'
                    }
                    
                    # Check if already invited
                    existing_emails = [p['email'] for p in session['participants']]
                    if participant_email not in existing_emails:
                        st.session_state.cupping_sessions[session_index]['participants'].append(new_participant)
                        save_data()
                        st.success(f"✅ Added {participant_name} to participant list!")
                        st.rerun()
                    else:
                        st.error("❌ This participant is already invited!")
                else:
                    st.error("❌ Please fill in both email and name")
            
            if send_invite and participant_email:
                try:
                    invite_pdf = generate_participant_invite_pdf(session, participant_email)
                    st.download_button(
                        label=f"📄 Download Invitation for {participant_email}",
                        data=invite_pdf,
                        file_name=f"cupping_invitation_{session['name'].replace(' ', '_')}_{participant_email.split('@')[0]}.pdf",
                        mime="application/pdf",
                        key=f"invite_pdf_{session_index}_{participant_email}"
                    )
                except Exception as e:
                    st.error(f"Error generating invitation: {e}")
    
    with col2:
        st.markdown("#### 👥 Current Participants")
        if session.get('participants'):
            for i, participant in enumerate(session['participants']):
                with st.expander(f"👤 {participant['name']}", expanded=False):
                    st.write(f"**Email:** {participant['email']}")
                    st.write(f"**Role:** {participant['role']}")
                    st.write(f"**Invited:** {participant['invited_date']}")
                    st.write(f"**Status:** {participant['status']}")
                    
                    col_x, col_y = st.columns(2)
                    with col_x:
                        if st.button(f"📧 Resend", key=f"resend_{session_index}_{i}"):
                            try:
                                invite_pdf = generate_participant_invite_pdf(session, participant['email'])
                                st.download_button(
                                    label="📄 Download Invitation",
                                    data=invite_pdf,
                                    file_name=f"cupping_invitation_{session['name'].replace(' ', '_')}_{participant['email'].split('@')[0]}.pdf",
                                    mime="application/pdf",
                                    key=f"resend_pdf_{session_index}_{i}"
                                )
                            except Exception as e:
                                st.error(f"Error: {e}")
                    
                    with col_y:
                        if st.button(f"🗑️ Remove", key=f"remove_participant_{session_index}_{i}"):
                            st.session_state.cupping_sessions[session_index]['participants'].pop(i)
                            save_data()
                            st.success("Participant removed")
                            st.rerun()
        else:
            st.info("No participants invited yet")
    
    # Session summary with participants
    st.markdown("#### 📋 Session Overview")
    participant_count = len(session.get('participants', []))
    total_participants = participant_count + 1  # +1 for lead cupper
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Participants", total_participants)
    with col2:
        st.metric("Invited Participants", participant_count)
    with col3:
        cups_needed = len(session['samples']) * session['cups_per_sample'] * total_participants
        st.metric("Total Cups Needed", cups_needed)
    
    # Quick actions
    st.markdown("#### ⚡ Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📧 Generate All Invites", use_container_width=True):
            if session.get('participants'):
                st.info("Click 'Generate Invite PDF' for each participant above to download individual invitations.")
            else:
                st.warning("No participants to invite yet!")
    
    with col2:
        if st.button("📊 Export Participant List", use_container_width=True):
            if session.get('participants'):
                participant_data = []
                for p in session['participants']:
                    participant_data.append(f"{p['name']} ({p['email']}) - {p['role']}")
                
                participant_list = "\\n".join(participant_data)
                st.text_area("Participant List (copy this):", participant_list, height=100)
            else:
                st.warning("No participants to export!")
    
    with col3:
        if st.button("❌ Close", use_container_width=True):
            del st.session_state.inviting_session
            st.rerun()

def show_edit_interface(session_index):
    st.markdown("---")
    st.subheader("✏️ Edit Cupping Session")
    
    session = st.session_state.cupping_sessions[session_index]
    st.markdown(f"### Editing: {session['name']}")
    
    if session.get('status') == 'Scored':
        st.warning("⚠️ **Note:** This session has been scored. Editing will preserve existing scores but you can modify session details.")
    
    with st.form(f"edit_session_{session_index}"):
        # Session details
        st.markdown("### 📋 Session Information")
        col1, col2 = st.columns(2)
        
        with col1:
            session_name = st.text_input("Session Name *", value=session['name'])
            cupping_date = st.date_input("Cupping Date", value=datetime.strptime(session['date'], '%Y-%m-%d').date())
            
            # Get current number of samples and cups
            current_samples = len(session['samples'])
            current_cups = session['cups_per_sample']
            
            num_samples = st.number_input("Number of Samples", 1, 8, current_samples)
            cups_per_sample = st.number_input("Cups per Sample", 3, 5, current_cups)
        
        with col2:
            cupper_name = st.text_input("Lead Cupper", value=session['cupper'])
            evaluation_type = st.selectbox("Protocol", ["SCA Standard", "COE Protocol", "Custom"], 
                                         index=["SCA Standard", "COE Protocol", "Custom"].index(session['protocol']) if session['protocol'] in ["SCA Standard", "COE Protocol", "Custom"] else 0)
            is_blind = st.checkbox("Blind Cupping", value=session['blind'])
            water_temp = st.number_input("Water Temperature (°C)", 90, 96, session['water_temp'])
        
        # Sample information
        st.markdown("### 🌱 Sample Information")
        samples = []
        
        for i in range(num_samples):
            st.markdown(f"**Sample {i+1}:**")
            col1, col2, col3 = st.columns(3)
            
            # Get existing sample data if available
            existing_sample = session['samples'][i] if i < len(session['samples']) else {
                'name': '', 'origin': '', 'variety': '', 'process': 'Washed', 'altitude': '', 'harvest_year': ''
            }
            
            with col1:
                sample_name = st.text_input(f"Sample Name", value=existing_sample['name'], key=f"edit_sample_name_{i}")
                origin = st.text_input(f"Origin", value=existing_sample['origin'], key=f"edit_origin_{i}")
            
            with col2:
                variety = st.text_input(f"Variety", value=existing_sample['variety'], key=f"edit_variety_{i}")
                process_options = ["Washed", "Natural", "Honey", "Pulped Natural"]
                process_index = process_options.index(existing_sample['process']) if existing_sample['process'] in process_options else 0
                process = st.selectbox(f"Process", process_options, index=process_index, key=f"edit_process_{i}")
            
            with col3:
                altitude = st.text_input(f"Altitude (masl)", value=existing_sample['altitude'], key=f"edit_altitude_{i}")
                harvest_year = st.text_input(f"Harvest Year", value=existing_sample['harvest_year'], key=f"edit_harvest_{i}")
            
            samples.append({
                'name': sample_name,
                'origin': origin,
                'variety': variety,
                'process': process,
                'altitude': altitude,
                'harvest_year': harvest_year
            })
            
            if i < num_samples - 1:
                st.markdown("---")
        
        # Show warning if reducing samples
        if num_samples < len(session['samples']):
            st.warning(f"⚠️ **Warning:** You are reducing samples from {len(session['samples'])} to {num_samples}. This will remove the last {len(session['samples']) - num_samples} sample(s) and any associated scores.")
        
        # Form buttons
        col1, col2 = st.columns(2)
        with col1:
            save_changes = st.form_submit_button("💾 Save Changes", use_container_width=True)
        with col2:
            cancel_edit = st.form_submit_button("❌ Cancel", use_container_width=True)
        
        if save_changes:
            if not session_name:
                st.error("❌ Session name is required")
            else:
                # Update session data
                updated_session = {
                    'name': session_name,
                    'date': cupping_date.strftime('%Y-%m-%d'),
                    'cupper': cupper_name,
                    'protocol': evaluation_type,
                    'blind': is_blind,
                    'water_temp': water_temp,
                    'samples': samples,
                    'cups_per_sample': cups_per_sample,
                    'created': session['created'],  # Keep original creation date
                    'status': session['status'],  # Keep current status
                    'last_modified': datetime.now().strftime('%Y-%m-%d %H:%M')
                }
                
                # Preserve existing scores if session was scored and samples weren't reduced
                if session.get('status') == 'Scored' and 'scores' in session:
                    if num_samples <= len(session['samples']):
                        # Keep existing scores, but only for remaining samples
                        existing_scores = session['scores'][:num_samples]
                        updated_session['scores'] = existing_scores
                        updated_session['session_notes'] = session.get('session_notes', '')
                        updated_session['scored_date'] = session.get('scored_date', '')
                    else:
                        # If adding samples, session needs to be re-scored
                        updated_session['status'] = 'Created'
                        st.warning("⚠️ **Note:** New samples added. Session status changed to 'Created' and needs to be re-scored.")
                
                # Preserve participants if they exist
                if 'participants' in session:
                    updated_session['participants'] = session['participants']
                
                # Update session in state
                st.session_state.cupping_sessions[session_index] = updated_session
                save_data()
                
                st.success("✅ Session updated successfully!")
                st.balloons()
                
                # Close edit interface
                del st.session_state.editing_session
                st.rerun()
        
        if cancel_edit:
            del st.session_state.editing_session
            st.rerun()
    
    # Show current session summary
    st.markdown("---")
    st.markdown("#### 📋 Current Session Summary")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Original Samples", len(session['samples']))
    with col2:
        st.metric("Current Status", session['status'])
    with col3:
        if 'participants' in session:
            st.metric("Participants", len(session['participants']))
        else:
            st.metric("Participants", 0)

def show_session_results(session_index):
    st.markdown("---")
    st.subheader("📈 Session Results")
    
    session = st.session_state.cupping_sessions[session_index]
    
    if 'scores' in session:
        st.markdown(f"### ☕ {session['name']} - Results")
        st.markdown(f"**📅 Scored:** {session.get('scored_date', 'Unknown')}")
        
        # Summary table
        scores_data = []
        for score in session['scores']:
            scores_data.append({
                'Sample': score['sample_name'],
                'Total': f"{score['total']:.2f}",
                'Fragrance': score['fragrance'],
                'Flavor': score['flavor'],
                'Aftertaste': score['aftertaste'],
                'Acidity': score['acidity'],
                'Body': score['body'],
                'Balance': score['balance'],
                'Overall': score['overall']
            })
        
        st.table(scores_data)
        
        # Best sample
        best_sample = max(session['scores'], key=lambda x: x['total'])
        st.success(f"🏆 Highest Score: {best_sample['sample_name']} - {best_sample['total']:.2f} points")
        
        # Individual sample details
        st.markdown("### 📋 Detailed Scores")
        for score in session['scores']:
            with st.expander(f"{score['sample_name']} - {score['total']:.2f} points"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Fragrance/Aroma:** {score['fragrance']}")
                    st.write(f"**Flavor:** {score['flavor']}")
                    st.write(f"**Aftertaste:** {score['aftertaste']}")
                    st.write(f"**Acidity:** {score['acidity']}")
                    st.write(f"**Body:** {score['body']}")
                with col2:
                    st.write(f"**Balance:** {score['balance']}")
                    st.write(f"**Uniformity:** {score['uniformity']}")
                    st.write(f"**Clean Cup:** {score['clean_cup']}")
                    st.write(f"**Sweetness:** {score['sweetness']}")
                    st.write(f"**Overall:** {score['overall']}")
                
                if score['defects'] > 0:
                    st.write(f"**Defects:** -{score['defects']}")
                
                if score['notes']:
                    st.markdown("**Tasting Notes:**")
                    st.write(score['notes'])
        
        # Session notes
        if session.get('session_notes'):
            st.markdown("### 📝 Session Notes")
            st.write(session['session_notes'])
        
        if st.button("Close Results"):
            del st.session_state.results_session
            st.rerun()
    else:
        st.error("No scores found for this session")

def show_login_form():
    st.markdown("### 🔐 Login to Your Account")
    st.info("""**Available Login Options:**

**Demo Account:**
📧 demo@coffee.com / demo123

**Test Users:**
📧 test@coffee.com / test123
📧 user@example.com / user123

Or create your own account in the Register tab.""")
    
    email = st.text_input("Email Address", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")
    remember = st.checkbox("🔒 Remember me")
    
    if st.button("🚀 Login", use_container_width=True):
        # Check demo credentials
        if email == "demo@coffee.com" and password == "demo123":
            st.session_state.logged_in = True
            st.session_state.user_data = {
                'name': 'Demo User',
                'email': email,
                'company': 'Coffee Cultura LLC',
                'role': 'Q Grader',
                'user_type': 'demo'
            }
            st.success("✅ Demo login successful!")
            st.rerun()
        
        # Check registered users
        elif 'registered_users' in st.session_state and email in st.session_state.registered_users:
            stored_user = st.session_state.registered_users[email]
            if stored_user['password'] == password:
                st.session_state.logged_in = True
                st.session_state.user_data = {
                    'name': stored_user['name'],
                    'email': email,
                    'company': stored_user['company'],
                    'role': stored_user['role'],
                    'user_type': 'registered'
                }
                st.success("✅ Login successful!")
                st.rerun()
            else:
                st.error("❌ Invalid password")
        else:
            st.error("❌ User not found. Please register or use demo credentials.")

def show_register_form():
    st.markdown("### 🆕 Create New Account")
    
    st.info("💡 **Usuarios de prueba disponibles:**\n\n📧 test@coffee.com / test123\n📧 user@example.com / user123")
    
    with st.form("registration_form"):
        st.markdown("#### 👤 Personal Information")
        full_name = st.text_input("Full Name *")
        email = st.text_input("Email Address *")
        
        st.markdown("#### 🔐 Security")
        password = st.text_input("Password *", type="password", help="Minimum 6 characters")
        confirm_password = st.text_input("Confirm Password *", type="password")
        
        st.markdown("#### ☕ Professional Information")
        company = st.text_input("Company/Organization")
        role = st.selectbox("Your Role", [
            "Coffee Enthusiast", "Home Barista", "Professional Barista",
            "Q Grader", "Coffee Roaster", "Café Owner", "Coffee Trader",
            "Coffee Producer", "Coffee Consultant", "Other"
        ])
        
        experience = st.selectbox("Cupping Experience", [
            "Beginner", "Intermediate", "Advanced", "Expert"
        ])
        
        terms = st.checkbox("✅ I agree to the Terms of Service *")
        
        if st.form_submit_button("🚀 Create Account", use_container_width=True):
            errors = []
            
            if not full_name.strip():
                errors.append("❌ Full name is required")
            if not email.strip():
                errors.append("❌ Email is required")
            elif "@" not in email:
                errors.append("❌ Valid email required")
            if not password:
                errors.append("❌ Password is required")
            elif len(password) < 6:
                errors.append("❌ Password must be 6+ characters")
            if password != confirm_password:
                errors.append("❌ Passwords don't match")
            if not terms:
                errors.append("❌ Must accept terms")
            
            # Check if email exists
            if ('registered_users' in st.session_state and 
                email in st.session_state.registered_users):
                errors.append("❌ Email already registered")
            if email == "demo@coffee.com":
                errors.append("❌ Email reserved for demo")
            
            if errors:
                for error in errors:
                    st.error(error)
            else:
                # Create user
                if 'registered_users' not in st.session_state:
                    st.session_state.registered_users = {}
                
                new_user = {
                    'name': full_name.strip(),
                    'password': password,
                    'company': company.strip() or "Independent",
                    'role': role,
                    'experience': experience,
                    'created': datetime.now().strftime('%Y-%m-%d %H:%M')
                }
                
                st.session_state.registered_users[email] = new_user
                
                st.success("✅ Account created successfully!")
                st.success("🎉 Welcome to the Coffee Cupping Community!")
                st.info("You can now login with your credentials in the Login tab.")
                st.warning("⚠️ **Note:** Your account will persist during this browser session. For permanent storage, bookmark this app and use the test accounts provided.")

def show_guest_mode():
    st.markdown("### 👥 Guest Mode")
    
    st.info("""
    **Guest Mode Features:**
    - ✅ Full app functionality
    - ✅ Create cupping sessions
    - ✅ Score sessions with SCA protocol
    - ✅ Coffee bag evaluations
    - ✅ Flavor wheel access
    - ⚠️ Data not saved permanently
    """)
    
    guest_name = st.text_input("Your Name (Optional)", placeholder="Coffee Lover")
    
    if st.button("🚀 Enter as Guest", use_container_width=True):
        st.session_state.logged_in = True
        st.session_state.user_data = {
            'name': guest_name or 'Guest User',
            'email': 'guest@demo.com',
            'company': 'Guest Session',
            'role': 'Coffee Enthusiast',
            'user_type': 'guest'
        }
        st.success("✅ Welcome, Guest!")
        st.rerun()

if __name__ == "__main__":
    main()