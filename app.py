import streamlit as st
from datetime import datetime

# Initialize session state for messages
if 'messages' not in st.session_state:
    st.session_state.messages = []

def main():
    st.title("POST Data Monitor")
    
    # Add endpoint info
    st.info("✨ Your webhook URL: https://your-app-name.streamlit.app/")
    
    # Clear button
    if st.button("Clear Messages"):
        st.session_state.messages = []
        st.rerun()
    
    # Get POST data if any
    try:
        body = st.query_params.get("body", None)
        if body:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state.messages.append({"time": timestamp, "data": body})
    except Exception as e:
        st.error(f"Error processing POST data: {e}")
    
    # Display messages
    for msg in reversed(st.session_state.messages):
        st.subheader(f"📩 Message received at {msg['time']}")
        st.code(msg['data'])
        st.divider()
    
    # Auto refresh
    st.empty()
    st.markdown(
        '<meta http-equiv="refresh" content="3">', 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
