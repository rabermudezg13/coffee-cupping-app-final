"""
Sharing functionality for Coffee Cupping App
"""
import streamlit as st
import base64
from io import BytesIO
import qrcode
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import Dict, Optional
import tempfile
import os
from database.db_manager import db
from config import SHARE_URL_BASE
from urllib.parse import quote

class SharingManager:
    def __init__(self):
        self.base_url = SHARE_URL_BASE
    
    def generate_share_url(self, share_id: str) -> str:
        """Generate shareable URL for cupping session"""
        return f"{self.base_url}?share={share_id}"
    
    def create_share_card_image(self, session_data: Dict) -> Optional[str]:
        """Create a beautiful share card image for social media"""
        try:
            # Create figure with modern design
            fig, ax = plt.subplots(figsize=(12, 8))
            fig.patch.set_facecolor('#1a1a1a')
            ax.set_facecolor('#2d2d2d')
            
            # Remove axes
            ax.set_xlim(0, 10)
            ax.set_ylim(0, 8)
            ax.axis('off')
            
            # Main title
            session_name = session_data.get('name', 'Coffee Cupping Session')
            ax.text(5, 7.2, session_name, ha='center', va='center', 
                   fontsize=24, fontweight='bold', color='#D4AF37')
            
            # Coffee icon and subtitle
            ax.text(5, 6.6, '☕ Professional Cupping Results', ha='center', va='center',
                   fontsize=16, color='#CCCCCC')
            
            # Score section
            if 'scores' in session_data and session_data['scores']:
                scores = session_data['scores']
                avg_total = sum(score.get('total', 0) for score in scores) / len(scores)
                
                # Large score display
                score_color = '#28a745' if avg_total >= 85 else '#ffc107' if avg_total >= 80 else '#dc3545'
                ax.text(2.5, 4.5, f"{avg_total:.1f}", ha='center', va='center',
                       fontsize=48, fontweight='bold', color=score_color)
                ax.text(2.5, 3.8, 'SCA SCORE', ha='center', va='center',
                       fontsize=12, fontweight='bold', color='#CCCCCC')
                
                # Grade
                if avg_total >= 90:
                    grade = "OUTSTANDING"
                    grade_color = '#FFD700'
                elif avg_total >= 85:
                    grade = "EXCELLENT"
                    grade_color = '#32CD32'
                elif avg_total >= 80:
                    grade = "VERY GOOD"
                    grade_color = '#1E90FF'
                else:
                    grade = "GOOD"
                    grade_color = '#FFA500'
                
                ax.text(2.5, 3.2, grade, ha='center', va='center',
                       fontsize=14, fontweight='bold', color=grade_color)
            
            # Sample info
            if 'samples' in session_data and session_data['samples']:
                sample_count = len(session_data['samples'])
                ax.text(7.5, 5.5, f"{sample_count}", ha='center', va='center',
                       fontsize=32, fontweight='bold', color='#D4AF37')
                ax.text(7.5, 5.0, 'SAMPLES', ha='center', va='center',
                       fontsize=12, fontweight='bold', color='#CCCCCC')
                
                # Show first sample details
                first_sample = session_data['samples'][0]
                origin = first_sample.get('origin', 'Unknown Origin')
                ax.text(7.5, 4.4, origin, ha='center', va='center',
                       fontsize=14, color='#CCCCCC', style='italic')
            
            # Cupping details
            cupper = session_data.get('cupper', 'Professional Cupper')
            if session_data.get('anonymous_mode'):
                cupper = 'Anonymous Taster'
            
            date = session_data.get('date', 'Recent')
            
            ax.text(5, 2.5, f"Cupped by: {cupper}", ha='center', va='center',
                   fontsize=12, color='#CCCCCC')
            ax.text(5, 2.1, f"Date: {date}", ha='center', va='center',
                   fontsize=12, color='#CCCCCC')
            
            # Top flavors
            if 'scores' in session_data:
                all_flavors = []
                for score in session_data['scores']:
                    if score.get('selected_flavors'):
                        all_flavors.extend(score['selected_flavors'])
                
                if all_flavors:
                    from collections import Counter
                    top_flavors = Counter(all_flavors).most_common(3)
                    flavor_text = " • ".join([flavor for flavor, _ in top_flavors])
                    ax.text(5, 1.5, f"Top Flavors: {flavor_text}", ha='center', va='center',
                           fontsize=11, color='#D4AF37', style='italic')
            
            # Footer
            ax.text(5, 0.8, 'Generated by Coffee Cupping App Professional', 
                   ha='center', va='center', fontsize=10, color='#888888')
            ax.text(5, 0.4, 'Share your cupping results with the world!', 
                   ha='center', va='center', fontsize=10, color='#888888')
            
            # Add decorative elements
            # Coffee bean shapes
            for i in range(5):
                x = 0.5 + i * 2
                y = 0.2
                bean = patches.Ellipse((x, y), 0.3, 0.1, angle=20, 
                                     facecolor='#8B4513', alpha=0.6)
                ax.add_patch(bean)
            
            plt.tight_layout()
            
            # Save to temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            plt.savefig(temp_file.name, dpi=300, bbox_inches='tight', 
                       facecolor='#1a1a1a', edgecolor='none')
            plt.close()
            temp_file.close()
            
            return temp_file.name
            
        except Exception as e:
            st.error(f"Error creating share card: {e}")
            return None
    
    def create_qr_code(self, url: str) -> Optional[str]:
        """Create QR code for sharing URL"""
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(url)
            qr.make(fit=True)
            
            # Create QR code image with custom styling
            img = qr.make_image(fill_color="#8B4513", back_color="white")
            
            # Save to temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            img.save(temp_file.name)
            temp_file.close()
            
            return temp_file.name
            
        except Exception as e:
            st.error(f"Error creating QR code: {e}")
            return None
    
    def generate_social_share_links(self, session_data: Dict, share_url: str) -> Dict:
        """Generate social media sharing links"""
        session_name = session_data.get('name', 'Coffee Cupping Session')
        
        # Calculate average score for text
        avg_score = 0
        if 'scores' in session_data and session_data['scores']:
            scores = session_data['scores']
            avg_score = sum(score.get('total', 0) for score in scores) / len(scores)
        
        # Create share text
        if avg_score >= 85:
            quality = "excellent"
        elif avg_score >= 80:
            quality = "very good"
        else:
            quality = "good"
        
        share_text = f"Just cupped {session_name} - scored {avg_score:.1f} points! This {quality} coffee shows amazing potential. ☕✨"
        
        # Encode for URLs
        encoded_text = quote(share_text)
        encoded_url = quote(share_url)
        
        return {
            'twitter': f"https://twitter.com/intent/tweet?text={encoded_text}&url={encoded_url}&hashtags=CoffeeCupping,SpecialtyCoffee,CoffeeReview",
            'facebook': f"https://www.facebook.com/sharer/sharer.php?u={encoded_url}",
            'linkedin': f"https://www.linkedin.com/sharing/share-offsite/?url={encoded_url}",
            'whatsapp': f"https://wa.me/?text={encoded_text}%20{encoded_url}",
            'telegram': f"https://t.me/share/url?url={encoded_url}&text={encoded_text}"
        }
    
    def render_sharing_interface(self, session_data: Dict, share_id: str):
        """Render the complete sharing interface"""
        st.markdown("### 🔗 Share This Cupping Session")
        
        share_url = self.generate_share_url(share_id)
        
        # URL display and copy
        col1, col2 = st.columns([3, 1])
        with col1:
            st.text_input("Share URL", value=share_url, key=f"share_url_{share_id}")
        with col2:
            if st.button("📋 Copy", key=f"copy_{share_id}"):
                st.write("✅ URL copied to clipboard!")
                # Log sharing event
                db.log_analytics_event('url_copied', session_id=share_id)
        
        st.markdown("---")
        
        # Visual share options
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📱 Social Media")
            social_links = self.generate_social_share_links(session_data, share_url)
            
            # Create social media buttons
            for platform, url in social_links.items():
                platform_icons = {
                    'twitter': '🐦',
                    'facebook': '📘',
                    'linkedin': '💼',
                    'whatsapp': '💬',
                    'telegram': '✈️'
                }
                
                if st.button(f"{platform_icons.get(platform, '🔗')} Share on {platform.title()}", 
                           key=f"social_{platform}_{share_id}"):
                    st.markdown(f'<a href="{url}" target="_blank">Opening {platform.title()}...</a>', 
                              unsafe_allow_html=True)
                    # Log social sharing event
                    db.log_analytics_event('social_share', session_id=share_id, 
                                         data={'platform': platform})
        
        with col2:
            st.markdown("#### 🖼️ Visual Sharing")
            
            if st.button("🎨 Generate Share Card", key=f"generate_card_{share_id}"):
                with st.spinner("Creating beautiful share card..."):
                    card_path = self.create_share_card_image(session_data)
                    if card_path:
                        st.image(card_path, caption="Share Card", use_column_width=True)
                        
                        # Provide download link
                        with open(card_path, "rb") as file:
                            btn = st.download_button(
                                label="📥 Download Share Card",
                                data=file.read(),
                                file_name=f"cupping_share_{share_id}.png",
                                mime="image/png"
                            )
                        
                        # Cleanup
                        try:
                            os.unlink(card_path)
                        except:
                            pass
                        
                        # Log card generation
                        db.log_analytics_event('share_card_generated', session_id=share_id)
            
            if st.button("📱 Generate QR Code", key=f"generate_qr_{share_id}"):
                with st.spinner("Creating QR code..."):
                    qr_path = self.create_qr_code(share_url)
                    if qr_path:
                        st.image(qr_path, caption="QR Code for Easy Sharing", width=200)
                        
                        # Provide download link
                        with open(qr_path, "rb") as file:
                            btn = st.download_button(
                                label="📥 Download QR Code",
                                data=file.read(),
                                file_name=f"cupping_qr_{share_id}.png",
                                mime="image/png"
                            )
                        
                        # Cleanup
                        try:
                            os.unlink(qr_path)
                        except:
                            pass
                        
                        # Log QR generation
                        db.log_analytics_event('qr_generated', session_id=share_id)
        
        # Analytics preview
        st.markdown("---")
        st.markdown("#### 📊 Sharing Analytics")
        
        # Get analytics for this session
        analytics_data = db.get_analytics_data()
        session_events = [event for event in analytics_data 
                         if event.get('session_id') == share_id]
        
        if session_events:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                url_copies = len([e for e in session_events if e.get('event_type') == 'url_copied'])
                st.metric("URL Copies", url_copies)
            
            with col2:
                social_shares = len([e for e in session_events if e.get('event_type') == 'social_share'])
                st.metric("Social Shares", social_shares)
            
            with col3:
                card_generations = len([e for e in session_events if e.get('event_type') == 'share_card_generated'])
                st.metric("Share Cards", card_generations)
        else:
            st.info("No sharing activity yet. Start sharing to see analytics!")

# Global sharing manager instance
sharing_manager = SharingManager()