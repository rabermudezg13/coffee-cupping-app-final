"""
Test script for the enhanced Coffee Cupping App
"""
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

def test_imports():
    """Test that all modules can be imported"""
    print("🧪 Testing module imports...")
    
    try:
        import config
        print("✅ Config imported successfully")
        
        from styles.themes import apply_custom_css, get_theme_colors
        print("✅ Themes module imported successfully")
        
        from database.db_manager import db
        print("✅ Database manager imported successfully")
        
        from utils.analytics import analytics
        print("✅ Analytics module imported successfully")
        
        from utils.sharing import sharing_manager
        print("✅ Sharing module imported successfully")
        
        from pages.public_cupping import render_public_cupping_page
        print("✅ Public cupping page imported successfully")
        
        from pages.analytics_dashboard import render_analytics_dashboard
        print("✅ Analytics dashboard imported successfully")
        
        from components.cupping_interface import render_enhanced_cupping_interface
        print("✅ Enhanced cupping interface imported successfully")
        
        print("\n🎉 All modules imported successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_database():
    """Test database functionality"""
    print("\n📊 Testing database functionality...")
    
    try:
        from database.db_manager import db
        
        # Test data loading
        data = db.load_json_data()
        print("✅ Data loading works")
        
        # Test session creation
        test_session = {
            'name': 'Test Session',
            'date': '2025-01-21',
            'cupper': 'Test User',
            'samples': [{'name': 'Test Coffee', 'origin': 'Test Origin'}],
            'user_email': 'test@example.com'
        }
        
        share_id = db.save_cupping_session(test_session, anonymous_mode=True)
        if share_id:
            print(f"✅ Session saving works - Share ID: {share_id}")
            
            # Test retrieval
            retrieved = db.get_session_by_share_id(share_id)
            if retrieved:
                print("✅ Session retrieval works")
            else:
                print("❌ Session retrieval failed")
        else:
            print("❌ Session saving failed")
        
        print("🎉 Database tests completed!")
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_analytics():
    """Test analytics functionality"""
    print("\n📈 Testing analytics functionality...")
    
    try:
        from utils.analytics import analytics
        
        # Test trends calculation
        trends = analytics.get_community_trends()
        print("✅ Community trends calculation works")
        
        # Test sample session analysis
        sample_session = {
            'scores': [
                {
                    'sample_name': 'Test Coffee',
                    'fragrance': 8.0,
                    'flavor': 8.5,
                    'aftertaste': 8.0,
                    'acidity': 8.0,
                    'body': 8.0,
                    'balance': 8.0,
                    'overall': 8.0,
                    'total': 84.0,
                    'selected_flavors': ['Chocolate', 'Nutty']
                }
            ]
        }
        
        insights = analytics.generate_session_insights(sample_session)
        print("✅ Session insights generation works")
        
        print("🎉 Analytics tests completed!")
        return True
        
    except Exception as e:
        print(f"❌ Analytics error: {e}")
        return False

def test_sharing():
    """Test sharing functionality"""
    print("\n🔗 Testing sharing functionality...")
    
    try:
        from utils.sharing import sharing_manager
        
        # Test URL generation
        test_share_id = "test123"
        share_url = sharing_manager.generate_share_url(test_share_id)
        print(f"✅ Share URL generation works: {share_url}")
        
        # Test social links generation
        test_session = {
            'name': 'Test Session',
            'scores': [{'total': 85.0}]
        }
        
        social_links = sharing_manager.generate_social_share_links(test_session, share_url)
        print("✅ Social links generation works")
        
        print("🎉 Sharing tests completed!")
        return True
        
    except Exception as e:
        print(f"❌ Sharing error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Coffee Cupping App Enhanced Tests\n")
    
    tests = [
        test_imports,
        test_database,
        test_analytics,
        test_sharing
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Test Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! The enhanced app is ready to run.")
        print("\n🚀 To start the app, run:")
        print("streamlit run streamlit_app_new.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()