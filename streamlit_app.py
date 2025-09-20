import streamlit as st
from datetime import datetime, date

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

def main():
    # Header
    st.markdown("""
    <div style="background: linear-gradient(135deg, #8B4513, #D2B48C); padding: 2rem; border-radius: 15px; text-align: center; margin-bottom: 2rem;">
        <h1 style="color: white; margin: 0; font-size: 3rem;">☕ Professional Coffee Cupping App</h1>
        <p style="color: #F5F5DC; margin: 0; font-size: 1.2rem;">SCA Protocol Implementation</p>
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
        
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Coffee Reviews"])
        
        with tab1:
            st.markdown("### 🔐 Login")
            st.info("**Demo Credentials:**\n\nEmail: demo@coffee.com\nPassword: demo123")
            
            email = st.text_input("Email Address")
            password = st.text_input("Password", type="password")
            
            if st.button("🚀 Login", use_container_width=True):
                if email == "demo@coffee.com" and password == "demo123":
                    st.session_state.logged_in = True
                    st.session_state.user_data = {
                        'name': 'Demo User',
                        'email': email,
                        'company': 'Coffee Cultura LLC'
                    }
                    st.success("✅ Login successful!")
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials. Use demo credentials above.")
        
        with tab2:
            st.markdown("### 📝 Coffee Bag Evaluation")
            st.info("Login to access the coffee evaluation features!")
        
        st.markdown('</div>', unsafe_allow_html=True)

def show_main_app():
    user_data = st.session_state.get('user_data', {})
    
    # Header with user info
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        st.markdown(f"## 👋 Welcome, {user_data.get('name', 'User')}!")
        
    with col2:
        st.markdown(f"📧 **{user_data.get('email', '')}**")
        st.markdown(f"🏢 **{user_data.get('company', '')}**")
    
    with col3:
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("### ☕ Navigation")
        page = st.radio("", ["📊 Dashboard", "☕ Cupping Sessions", "📝 Coffee Reviews", "👤 Profile"])
    
    # Main content
    if page == "📊 Dashboard":
        show_dashboard()
    elif page == "☕ Cupping Sessions":
        show_cupping_sessions()
    elif page == "📝 Coffee Reviews":
        show_coffee_reviews()
    elif page == "👤 Profile":
        show_profile()

def show_dashboard():
    st.title("📊 Dashboard")
    
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
                    # Store review
                    if 'coffee_reviews' not in st.session_state:
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
                    
                    st.session_state.coffee_reviews.append(review)
                    st.success("✅ Coffee review saved successfully!")
                    st.balloons()
    
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
    
    tab1, tab2, tab3, tab4 = st.tabs(["🆕 New Session", "📋 My Sessions", "📊 Analysis", "🎨 Flavor Wheel"])
    
    with tab1:
        show_new_cupping_session()
    
    with tab2:
        show_my_cupping_sessions()
    
    with tab3:
        show_cupping_analysis()
    
    with tab4:
        show_flavor_wheel()

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
                # Store session
                if 'cupping_sessions' not in st.session_state:
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
                
                st.session_state.cupping_sessions.append(session)
                st.success(f"✅ Created cupping session: '{session_name}' with {num_samples} samples")
                st.balloons()

def show_my_cupping_sessions():
    st.subheader("📋 My Cupping Sessions")
    
    if 'cupping_sessions' in st.session_state and st.session_state.cupping_sessions:
        for session in st.session_state.cupping_sessions:
            st.markdown(f'''
            <div class="coffee-card">
                <h4>☕ {session["name"]}</h4>
                <p><strong>📅 Date:</strong> {session["date"]} | <strong>👨‍🔬 Cupper:</strong> {session["cupper"]}</p>
                <p><strong>🔬 Protocol:</strong> {session["protocol"]} | <strong>🌡️ Water:</strong> {session["water_temp"]}°C</p>
                <p><strong>🌱 Samples:</strong> {len(session["samples"])} | <strong>☕ Cups/Sample:</strong> {session["cups_per_sample"]}</p>
                <p><strong>👁️ Blind:</strong> {"Yes" if session["blind"] else "No"} | <strong>📊 Status:</strong> {session["status"]}</p>
                <p style="font-size: 0.9rem; color: #666;"><strong>📅 Created:</strong> {session["created"]}</p>
            </div>
            ''', unsafe_allow_html=True)
            
            # Sample details
            with st.expander(f"📋 View samples - {session['name']}"):
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
    else:
        st.info("📝 No cupping sessions yet. Create your first professional cupping session!")

def show_cupping_analysis():
    st.subheader("📊 Cupping Analysis")
    
    if 'cupping_sessions' in st.session_state and st.session_state.cupping_sessions:
        sessions_count = len(st.session_state.cupping_sessions)
        total_samples = sum(len(s['samples']) for s in st.session_state.cupping_sessions)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Sessions", sessions_count)
        with col2:
            st.metric("Total Samples", total_samples)
        with col3:
            st.metric("Avg Samples/Session", f"{total_samples/sessions_count:.1f}" if sessions_count > 0 else "0")
        
        st.markdown("---")
        st.markdown("### 📈 Session Overview")
        
        for session in st.session_state.cupping_sessions:
            st.markdown(f"**{session['name']}** - {session['date']} - {len(session['samples'])} samples")
    else:
        st.info("📊 No cupping data yet. Create sessions to see analysis.")

def show_flavor_wheel():
    st.subheader("🎨 SCA Flavor Wheel")
    
    st.success("✅ SCA Flavor Wheel - Professional Implementation")
    
    # SCA Flavor categories
    flavor_categories = {
        "🍊 Fruity": {
            "Citrus": ["Grapefruit", "Orange", "Lemon", "Lime"],
            "Berry": ["Blackberry", "Raspberry", "Blueberry", "Strawberry"],
            "Stone Fruit": ["Peach", "Apricot", "Plum", "Cherry"],
            "Tropical": ["Pineapple", "Mango", "Papaya", "Coconut"]
        },
        "🌸 Floral": {
            "Floral": ["Rose", "Jasmine", "Lavender", "Chamomile"],
            "Tea-like": ["Black Tea", "Earl Grey"]
        },
        "🍯 Sweet": {
            "Brown Sugar": ["Molasses", "Maple Syrup", "Caramel", "Honey"],
            "Vanilla": ["Vanilla"],
            "Chocolate": ["Dark Chocolate", "Milk Chocolate"]
        },
        "🥜 Nutty": {
            "Tree Nuts": ["Almond", "Hazelnut", "Walnut", "Pecan"],
            "Legumes": ["Peanut"]
        },
        "🌿 Green/Vegetative": {
            "Fresh": ["Green", "Underripe"],
            "Dried": ["Hay", "Herb-like"]
        },
        "🔥 Roasted": {
            "Grain": ["Bread", "Malt", "Rice"],
            "Burnt": ["Smoky", "Ashy", "Acrid"]
        }
    }
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🎯 Select Flavor Descriptors")
        selected_flavors = []
        
        for category, subcategories in flavor_categories.items():
            with st.expander(category):
                for subcat, flavors in subcategories.items():
                    st.markdown(f"**{subcat}:**")
                    cols = st.columns(min(len(flavors), 3))
                    for i, flavor in enumerate(flavors):
                        with cols[i % len(cols)]:
                            if st.checkbox(flavor, key=f"flavor_{category}_{subcat}_{flavor}"):
                                selected_flavors.append(flavor)
    
    with col2:
        st.markdown("### 📋 Selected Flavors")
        if selected_flavors:
            for flavor in selected_flavors:
                st.markdown(f"🏷️ **{flavor}**")
            st.markdown(f"**Total:** {len(selected_flavors)}")
        else:
            st.info("Select flavors from the wheel")
        
        st.markdown("---")
        st.markdown("### 📖 SCA Guidelines")
        st.markdown("""
        - **Primary:** Most prominent notes
        - **Secondary:** Supporting flavors  
        - **Finish:** Aftertaste descriptors
        - **Limit:** 8-10 descriptors max
        """)

if __name__ == "__main__":
    main()