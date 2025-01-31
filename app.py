# streamlit_app.py
import streamlit as st
import requests
import json
from datetime import datetime

# Configure page settings
st.set_page_config(page_title="Message Receiver", page_icon="📨")

# Initialize session state for messages if it doesn't exist
if 'messages' not in st.session_state:
    st.session_state.messages = []

def main():
    st.title("Message Receiver")
    
    # Add some styling
    st.markdown("""
        <style>
        .message-container {
            padding: 10px;
            margin: 5px 0;
            border-radius: 5px;
            background-color: #f0f2f6;
        }
        </style>
    """, unsafe_allow_html=True)

    # Configuration section
    with st.sidebar:
        st.header("Configuration")
        api_url = st.text_input(
            "Flask API URL",
            value="https://gamkertestbot.onrender.com/messages",
            help="Enter your Render-hosted Flask API URL"
        )

    # Button to check for new messages
    if st.button("Check for New Messages"):
        try:
            # Make GET request to Flask API
            response = requests.get(api_url)
            
            if response.status_code == 200:
                new_messages = response.json()
                
                # Update session state with new messages
                if new_messages:
                    for msg in new_messages:
                        if msg not in st.session_state.messages:
                            st.session_state.messages.append(msg)
                    st.success("New messages retrieved successfully!")
                else:
                    st.info("No new messages available.")
            else:
                st.error(f"Error accessing API: Status code {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            st.error(f"Error connecting to API: {str(e)}")

    # Display messages
    if st.session_state.messages:
        st.header("Received Messages")
        for msg in reversed(st.session_state.messages):
            with st.container():
                st.markdown(f"""
                    <div class="message-container">
                        <strong>Time:</strong> {datetime.fromtimestamp(msg.get('timestamp', 0)).strftime('%Y-%m-%d %H:%M:%S')}<br>
                        <strong>Message:</strong> {msg.get('content', 'No content')}<br>
                        <strong>ID:</strong> {msg.get('id', 'No ID')}
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No messages received yet. Click 'Check for New Messages' to fetch new messages.")

    # Clear messages button
    if st.session_state.messages and st.button("Clear All Messages"):
        st.session_state.messages = []
        st.success("All messages cleared!")

if __name__ == "__main__":
    main()
