import streamlit as st
import json
from datetime import datetime

# Initialize session state for messages if it doesn't exist
if 'messages' not in st.session_state:
    st.session_state.messages = []

def main():
    st.title("Message Monitor")
    
    # Add API endpoint information
    st.info("Send POST requests to: https://your-app-name.streamlit.app/api/webhook")
    
    # Clear messages button
    if st.button("Clear All Messages"):
        st.session_state.messages = []
        st.experimental_rerun()

    # Display messages in reverse order (newest first)
    for msg in reversed(st.session_state.messages):
        try:
            with st.expander(f"Message from {msg['timestamp']}", expanded=True):
                st.json(msg['data'])
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
            
            # Add timestamp and save to session state
            message = {
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'data': data
            }
            st.session_state.messages.append(message)
            
            return {'status': 'success'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    st.experimental_handle_webhook('webhook', handle_webhook)

if __name__ == "__main__":
    main()
