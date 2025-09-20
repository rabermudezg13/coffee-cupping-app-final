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
        page = st.radio("", ["📊 Dashboard", "📝 Coffee Reviews", "👤 Profile"])
    
    # Main content
    if page == "📊 Dashboard":
        show_dashboard()
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

if __name__ == "__main__":
    main()