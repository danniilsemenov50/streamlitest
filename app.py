import streamlit as st
import requests
from PIL import Image
import io
import base64
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Message Center",
    page_icon="💬",
    layout="wide"
)

# Initialize session state
if 'last_message_count' not in st.session_state:
    st.session_state.last_message_count = 0

def decode_image(base64_string):
    """Convert base64 string back to image"""
    try:
        img_bytes = base64.b64decode(base64_string)
        return Image.open(io.BytesIO(img_bytes))
    except Exception as e:
        st.error(f"Error decoding image: {str(e)}")
        return None

def display_message(message):
    """Display a single message"""
    with st.container():
        # Message header
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"**Message ID:** {message['id'][:8]}...")
        with col2:
            st.write(f"**Time:** {datetime.fromtimestamp(message['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Message content
        if message['type'] == 'image':
            if message.get('text'):  # Optional text with image
                st.write(f"**Caption:** {message['text']}")
            if message.get('filename'):
                st.write(f"**File:** {message['filename']}")
            img = decode_image(message['image'])
            if img:
                st.image(img, use_container_width=True)
        else:  # Text message
            st.write(f"**From:** {message.get('sender', 'Unknown')}")
            st.write(message['text'])
        
        st.divider()

def main():
    st.title("Message Center")
    
    # API Configuration
    with st.sidebar:
        st.header("Settings")
        api_url = st.text_input(
            "Flask API Base URL",
            value="https://gamkertestbot.onrender.com",
            help="Enter the base URL of your Flask API"
        )
        auto_refresh = st.checkbox("Auto-refresh", value=True)
        if auto_refresh:
            refresh_interval = st.slider(
                "Refresh interval (seconds)",
                min_value=1,
                max_value=60,
                value=5
            )
        
        # Display options
        st.header("Display Options")
        show_images = st.checkbox("Show Images", value=True)
        show_text = st.checkbox("Show Text Messages", value=True)

    # Get messages from API
    try:
        response = requests.get(f"{api_url}/messages")
        if response.status_code == 200:
            current_messages = response.json()
            
            # Check for new messages
            if len(current_messages) > st.session_state.last_message_count:
                st.success(f"New messages received! Total: {len(current_messages)}")
                st.session_state.last_message_count = len(current_messages)
            
            # Display messages
            if current_messages:
                st.header(f"Messages ({len(current_messages)})")
                
                for message in reversed(current_messages):
                    if (message['type'] == 'image' and show_images) or \
                       (message['type'] == 'text' and show_text):
                        display_message(message)
            else:
                st.info("No messages received yet.")
                
        else:
            st.error(f"Error fetching messages: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to API: {str(e)}")

    # Auto-refresh
    if auto_refresh:
        st.empty()
        st.rerun()

if __name__ == "__main__":
    main()
