# main.py
import streamlit as st
import json
import pandas as pd
from datetime import datetime
import os

# Initialize session state for messages
if 'messages' not in st.session_state:
    st.session_state.messages = []

def save_message(message):
    """Save message to CSV file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message_data = {
        'timestamp': timestamp,
        'message': json.dumps(message)
    }
    
    df = pd.DataFrame([message_data])
    
    # Append to CSV file
    csv_path = 'messages.csv'
    if os.path.exists(csv_path):
        df.to_csv(csv_path, mode='a', header=False, index=False)
    else:
        df.to_csv(csv_path, index=False)

@st.cache_data(ttl=1)  # Cache for 1 second
def get_messages():
    """Read messages from CSV file"""
    try:
        if os.path.exists('messages.csv'):
            df = pd.read_csv('messages.csv')
            return df.to_dict('records')
    except Exception:
        return []
    return []

def main():
    st.title("Message Monitor")
    
    # Add API endpoint information
    st.info("Send POST requests to: https://gamkersrat101.streamlit.app/api")
    
    # Clear messages button
    if st.button("Clear All Messages"):
        if os.path.exists('messages.csv'):
            os.remove('messages.csv')
        st.session_state.messages = []
        st.experimental_rerun()

    # Display messages
    messages = get_messages()
    
    if messages:
        for msg in messages[::-1]:  # Show newest first
            try:
                with st.expander(f"Message from {msg['timestamp']}", expanded=False):
                    st.json(json.loads(msg['message']))
            except Exception as e:
                st.error(f"Error displaying message: {str(e)}")

    # Auto-refresh every few seconds
    st.empty()
    st.markdown("""
        <meta http-equiv="refresh" content="5">
        """, unsafe_allow_html=True)

# Handle incoming webhooks
headers = st.context.headers
if headers and 'webhook' in headers.get('path', ''):
    import asyncio
    async def handle_webhook():
        try:
            body = await asyncio.get_running_loop().run_in_executor(
                None, lambda: st.experimental_get_query_params().get('body', ['{}'])[0]
            )
            data = json.loads(body)
            save_message(data)
            return {'status': 'success'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    st.experimental_handle_webhook('webhook', handle_webhook)

if __name__ == "__main__":
    main()
