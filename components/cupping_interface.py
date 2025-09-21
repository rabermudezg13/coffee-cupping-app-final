"""
Enhanced cupping interface components
"""
import streamlit as st
import uuid
from datetime import datetime, date
from database.db_manager import db
from utils.sharing import sharing_manager
from styles.themes import get_theme_colors
from config import SCA_CATEGORIES, FLAVOR_CATEGORIES

def render_enhanced_cupping_interface():
    """Render the enhanced cupping interface"""
    colors = get_theme_colors()
    
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)
    
    # Header
    st.markdown(f"""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 class="modern-title">☕ Professional Cupping Session</h1>
        <p style="font-size: 1.2rem; color: {colors['text_secondary']};">
            Create and score your cupping session with enhanced features
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Tabs for different stages
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Session Setup",
        "☕ Sample Registration", 
        "🎯 Scoring",
        "🔗 Share & Export"
    ])
    
    with tab1:
        render_session_setup()
    
    with tab2:
        render_sample_registration()
    
    with tab3:
        render_scoring_interface()
    
    with tab4:
        render_share_export()
    
    st.markdown("</div>", unsafe_allow_html=True)

def render_session_setup():
    """Render session setup interface"""
    st.markdown("### 📋 Session Configuration")
    
    # Initialize session data
    if 'current_session' not in st.session_state:
        st.session_state.current_session = {
            'session_id': str(uuid.uuid4()),
            'name': '',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'cupper': '',
            'protocol': 'SCA Standard',
            'water_temp': 93,
            'cups_per_sample': 5,
            'blind': False,
            'status': 'Setup',
            'samples': [],
            'scores': [],
            'session_notes': '',
            'user_email': st.session_state.get('current_user', ''),
            'anonymous_mode': st.session_state.get('anonymous_mode', False)
        }
    
    # Session form
    col1, col2 = st.columns(2)
    
    with col1:
        session_name = st.text_input(
            "Session Name *",
            value=st.session_state.current_session['name'],
            placeholder="e.g., Colombian Single Origins Comparison"
        )
        st.session_state.current_session['name'] = session_name
        
        cupper_name = st.text_input(
            "Lead Cupper *",
            value=st.session_state.current_session['cupper'],
            placeholder="Your name"
        )
        st.session_state.current_session['cupper'] = cupper_name
        
        session_date = st.date_input(
            "Session Date",
            value=datetime.strptime(st.session_state.current_session['date'], '%Y-%m-%d').date()
        )
        st.session_state.current_session['date'] = session_date.strftime('%Y-%m-%d')
    
    with col2:
        protocol = st.selectbox(
            "Cupping Protocol",
            ["SCA Standard", "COE Protocol", "Custom"],
            index=0 if st.session_state.current_session['protocol'] == 'SCA Standard' else 1
        )
        st.session_state.current_session['protocol'] = protocol
        
        water_temp = st.slider(
            "Water Temperature (°C)",
            min_value=88,
            max_value=96,
            value=st.session_state.current_session['water_temp']
        )
        st.session_state.current_session['water_temp'] = water_temp
        
        cups_per_sample = st.slider(
            "Cups per Sample",
            min_value=3,
            max_value=8,
            value=st.session_state.current_session['cups_per_sample']
        )
        st.session_state.current_session['cups_per_sample'] = cups_per_sample
    
    # Advanced options
    with st.expander("🔧 Advanced Options"):
        blind_cupping = st.checkbox(
            "Blind Cupping",
            value=st.session_state.current_session['blind'],
            help="Hide sample identities during cupping"
        )
        st.session_state.current_session['blind'] = blind_cupping
        
        # Anonymous mode toggle
        anonymous_mode = st.checkbox(
            "🕶️ Anonymous Mode",
            value=st.session_state.current_session['anonymous_mode'],
            help="Hide your identity in shared results"
        )
        st.session_state.current_session['anonymous_mode'] = anonymous_mode
        
        session_notes = st.text_area(
            "Session Notes",
            value=st.session_state.current_session['session_notes'],
            placeholder="Any notes about the session setup, environment, etc."
        )
        st.session_state.current_session['session_notes'] = session_notes
    
    # Validation
    if session_name and cupper_name:
        st.success("✅ Session configuration complete! Move to Sample Registration.")
    else:
        st.warning("⚠️ Please fill in all required fields marked with *")

def render_sample_registration():
    """Render sample registration interface"""
    st.markdown("### ☕ Sample Registration")
    
    if not st.session_state.get('current_session', {}).get('name'):
        st.warning("⚠️ Please complete Session Setup first.")
        return
    
    # Add new sample form
    with st.expander("➕ Add New Sample", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            sample_name = st.text_input("Sample Name *", placeholder="e.g., Huila Supremo")
            origin = st.text_input("Origin", placeholder="e.g., Colombia, Huila")
            variety = st.text_input("Variety", placeholder="e.g., Caturra, Typica")
        
        with col2:
            process = st.selectbox(
                "Processing Method",
                ["Washed", "Natural", "Honey", "Semi-washed", "Other"]
            )
            altitude = st.text_input("Altitude", placeholder="e.g., 1,200-1,400 masl")
            harvest_year = st.selectbox(
                "Harvest Year",
                [str(year) for year in range(datetime.now().year, datetime.now().year - 5, -1)]
            )
        
        if st.button("➕ Add Sample") and sample_name:
            new_sample = {
                'name': sample_name,
                'origin': origin,
                'variety': variety,
                'process': process,
                'altitude': altitude,
                'harvest_year': harvest_year
            }
            st.session_state.current_session['samples'].append(new_sample)
            st.success(f"✅ Added sample: {sample_name}")
            st.rerun()
    
    # Display current samples
    samples = st.session_state.current_session.get('samples', [])
    
    if samples:
        st.markdown(f"### 📋 Registered Samples ({len(samples)})")
        
        for i, sample in enumerate(samples):
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.markdown(f"**{sample['name']}**")
                st.caption(f"{sample['origin']} | {sample['variety']} | {sample['process']}")
            
            with col2:
                if st.button("✏️ Edit", key=f"edit_sample_{i}"):
                    st.session_state[f"editing_sample_{i}"] = True
            
            with col3:
                if st.button("🗑️ Remove", key=f"remove_sample_{i}"):
                    st.session_state.current_session['samples'].pop(i)
                    st.rerun()
            
            # Edit form
            if st.session_state.get(f"editing_sample_{i}"):
                with st.form(f"edit_form_{i}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        new_name = st.text_input("Name", value=sample['name'])
                        new_origin = st.text_input("Origin", value=sample['origin'])
                        new_variety = st.text_input("Variety", value=sample['variety'])
                    
                    with col2:
                        new_process = st.selectbox("Process", 
                                                 ["Washed", "Natural", "Honey", "Semi-washed", "Other"],
                                                 index=["Washed", "Natural", "Honey", "Semi-washed", "Other"].index(sample['process']) if sample['process'] in ["Washed", "Natural", "Honey", "Semi-washed", "Other"] else 0)
                        new_altitude = st.text_input("Altitude", value=sample['altitude'])
                        new_harvest = st.text_input("Harvest Year", value=sample['harvest_year'])
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("💾 Save Changes"):
                            st.session_state.current_session['samples'][i] = {
                                'name': new_name,
                                'origin': new_origin,
                                'variety': new_variety,
                                'process': new_process,
                                'altitude': new_altitude,
                                'harvest_year': new_harvest
                            }
                            del st.session_state[f"editing_sample_{i}"]
                            st.rerun()
                    
                    with col2:
                        if st.form_submit_button("❌ Cancel"):
                            del st.session_state[f"editing_sample_{i}"]
                            st.rerun()
        
        # Ready to score
        if samples:
            if st.button("🎯 Start Scoring", type="primary", use_container_width=True):
                st.session_state.current_session['status'] = 'Ready to Score'
                st.success("✅ Samples registered! Move to Scoring tab.")
    
    else:
        st.info("➕ Add your first sample to get started.")

def render_scoring_interface():
    """Render enhanced scoring interface"""
    st.markdown("### 🎯 Cupping Scores")
    
    session = st.session_state.get('current_session', {})
    samples = session.get('samples', [])
    
    if not samples:
        st.warning("⚠️ Please register samples first.")
        return
    
    # Sample selection for scoring
    selected_sample_idx = st.selectbox(
        "Select Sample to Score",
        range(len(samples)),
        format_func=lambda x: f"{x+1}. {samples[x]['name']}"
    )
    
    selected_sample = samples[selected_sample_idx]
    
    # Find existing score or create new one
    existing_score_idx = None
    for i, score in enumerate(session.get('scores', [])):
        if score['sample_name'] == selected_sample['name']:
            existing_score_idx = i
            break
    
    if existing_score_idx is not None:
        current_score = session['scores'][existing_score_idx]
    else:
        current_score = {
            'sample_name': selected_sample['name'],
            'fragrance': 6.0,
            'flavor': 6.0,
            'aftertaste': 6.0,
            'acidity': 6.0,
            'body': 6.0,
            'balance': 6.0,
            'uniformity': 10.0,
            'clean_cup': 10.0,
            'sweetness': 10.0,
            'overall': 6.0,
            'defects': 0.0,
            'total': 0.0,
            'notes': '',
            'selected_flavors': []
        }
    
    # Scoring interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"#### 📊 Scoring: {selected_sample['name']}")
        
        # Primary attributes (6-10 scale)
        primary_attrs = ['fragrance', 'flavor', 'aftertaste', 'acidity', 'body', 'balance', 'overall']
        
        for attr in primary_attrs:
            current_score[attr] = st.slider(
                f"{attr.replace('_', ' ').title()}",
                min_value=6.0,
                max_value=10.0,
                value=float(current_score[attr]),
                step=0.25,
                key=f"{selected_sample['name']}_{attr}"
            )
        
        st.markdown("---")
        
        # Secondary attributes (usually 10)
        col1_sec, col2_sec = st.columns(2)
        
        with col1_sec:
            current_score['uniformity'] = st.slider(
                "Uniformity",
                min_value=6.0,
                max_value=10.0,
                value=float(current_score['uniformity']),
                step=2.0,
                key=f"{selected_sample['name']}_uniformity"
            )
            
            current_score['clean_cup'] = st.slider(
                "Clean Cup",
                min_value=6.0,
                max_value=10.0,
                value=float(current_score['clean_cup']),
                step=2.0,
                key=f"{selected_sample['name']}_clean_cup"
            )
        
        with col2_sec:
            current_score['sweetness'] = st.slider(
                "Sweetness",
                min_value=6.0,
                max_value=10.0,
                value=float(current_score['sweetness']),
                step=2.0,
                key=f"{selected_sample['name']}_sweetness"
            )
            
            current_score['defects'] = st.slider(
                "Defects (deduction)",
                min_value=0.0,
                max_value=8.0,
                value=float(current_score['defects']),
                step=2.0,
                key=f"{selected_sample['name']}_defects"
            )
    
    with col2:
        # Calculate total dynamically
        total = (
            current_score['fragrance'] + current_score['flavor'] + 
            current_score['aftertaste'] + current_score['acidity'] + 
            current_score['body'] + current_score['balance'] + 
            current_score['uniformity'] + current_score['clean_cup'] + 
            current_score['sweetness'] + current_score['overall'] - 
            current_score['defects']
        )
        current_score['total'] = total
        
        # Score display
        colors = get_theme_colors()
        if total >= 90:
            score_color = colors['success']
            grade = "🏆 Outstanding"
        elif total >= 85:
            score_color = colors['primary']
            grade = "⭐ Excellent"
        elif total >= 80:
            score_color = colors['warning']
            grade = "👍 Very Good"
        else:
            score_color = colors['error']
            grade = "👌 Good"
        
        st.markdown(f"""
        <div class="score-container" style="text-align: center; margin-bottom: 1rem;">
            <h2 style="color: {score_color}; margin: 0;">{total:.2f}</h2>
            <p style="color: {colors['text_secondary']}; margin: 0;">SCA Score</p>
            <p style="color: {score_color}; font-weight: bold; margin: 0;">{grade}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Progress towards next grade
        if total < 90:
            next_grade = 90 if total >= 85 else 85 if total >= 80 else 80
            points_needed = next_grade - total
            st.info(f"📈 {points_needed:.1f} points to next grade")
    
    # Flavor selection
    st.markdown("---")
    st.markdown("#### 🍃 Flavor Profile")
    
    # Flavor wheel selection
    selected_flavors = current_score.get('selected_flavors', [])
    
    # Group flavors by category
    flavor_cols = st.columns(3)
    
    for i, (category, data) in enumerate(FLAVOR_CATEGORIES.items()):
        with flavor_cols[i % 3]:
            st.markdown(f"**{category}**")
            
            for subcat, flavors in data['subcategories'].items():
                with st.expander(subcat):
                    for flavor in flavors:
                        if st.checkbox(flavor, 
                                     value=flavor in selected_flavors,
                                     key=f"{selected_sample['name']}_flavor_{flavor}"):
                            if flavor not in selected_flavors:
                                selected_flavors.append(flavor)
                        else:
                            if flavor in selected_flavors:
                                selected_flavors.remove(flavor)
    
    current_score['selected_flavors'] = selected_flavors
    
    # Tasting notes
    st.markdown("#### 📝 Tasting Notes")
    current_score['notes'] = st.text_area(
        "Additional notes and observations",
        value=current_score['notes'],
        placeholder="Describe aroma, flavor, mouthfeel, and overall impression...",
        key=f"{selected_sample['name']}_notes"
    )
    
    # Save score
    if st.button("💾 Save Score", type="primary", use_container_width=True):
        if existing_score_idx is not None:
            st.session_state.current_session['scores'][existing_score_idx] = current_score
        else:
            if 'scores' not in st.session_state.current_session:
                st.session_state.current_session['scores'] = []
            st.session_state.current_session['scores'].append(current_score)
        
        st.success(f"✅ Score saved for {selected_sample['name']}")
        
        # Update session status
        total_samples = len(samples)
        scored_samples = len(st.session_state.current_session.get('scores', []))
        
        if scored_samples == total_samples:
            st.session_state.current_session['status'] = 'Scored'
            st.balloons()
            st.success("🎉 All samples scored! Session complete!")

def render_share_export():
    """Render sharing and export interface"""
    st.markdown("### 🔗 Share & Export")
    
    session = st.session_state.get('current_session', {})
    
    if session.get('status') != 'Scored':
        st.warning("⚠️ Complete scoring first to enable sharing and export.")
        return
    
    # Save session to database first
    if not session.get('share_id'):
        share_id = db.save_cupping_session(
            session, 
            anonymous_mode=session.get('anonymous_mode', False)
        )
        if share_id:
            st.session_state.current_session['share_id'] = share_id
            st.success("✅ Session saved! Sharing enabled.")
        else:
            st.error("❌ Error saving session.")
            return
    
    # Sharing interface
    sharing_manager.render_sharing_interface(session, session['share_id'])
    
    # Reset session option
    st.markdown("---")
    st.markdown("### 🔄 Session Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📋 Start New Session", type="secondary"):
            # Clear current session
            keys_to_remove = [key for key in st.session_state.keys() if key.startswith('current_session')]
            for key in keys_to_remove:
                del st.session_state[key]
            st.success("✅ Ready for new session!")
            st.rerun()
    
    with col2:
        if st.button("📊 View in Analytics", type="secondary"):
            st.session_state.current_page = '📊 Analytics'
            st.rerun()