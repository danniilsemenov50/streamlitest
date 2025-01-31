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

# [Previous CSS and configuration remains the same]

def commands_page():
    st.title("🖥️ Remote Command Execution")
    
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
                    response = requests.post(f"{API_URL}/send_message", json={"command": command, "type": "command"})
                    if response.status_code == 200:
                        st.subheader("Command Output")
                        output_response = requests.get(f"{API_URL}/get_messages")
                        if output_response.status_code == 200:
                            messages = output_response.json()
                            for msg in reversed(messages):
                                if msg.get('type') == 'command_output':
                                    st.code(msg.get('message', 'No output'), language='bash')
                                    break
                    else:
                        st.error("Failed to execute command")
        
        # Refresh Command Output
        if st.button("Refresh Command Output"):
            try:
                output_response = requests.get(f"{API_URL}/get_messages")
                if output_response.status_code == 200:
                    messages = output_response.json()
                    for msg in reversed(messages):
                        if msg.get('type') == 'command_output':
                            st.subheader("Last Command Output")
                            st.code(msg.get('message', 'No output'), language='bash')
                            break
                else:
                    st.error("Failed to retrieve command output")
            except Exception as e:
                st.error(f"Error retrieving output: {str(e)}")

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
        if st.button("Get Screenshot"):
            try:
                response = requests.post(f"{API_URL}/send_message", json={"type": "screenshot"})
                if response.status_code == 200:
                    output_response = requests.get(f"{API_URL}/get_messages")
                    if output_response.status_code == 200:
                        messages = output_response.json()
                        for msg in reversed(messages):
                            if msg.get('type') == 'screenshot':
                                screenshot_data = msg.get('image')
                                if screenshot_data:
                                    img_bytes = base64.b64decode(screenshot_data)
                                    img = Image.open(io.BytesIO(img_bytes))
                                    st.image(img, caption="Remote Screenshot", use_column_width=True)
                                break
                else:
                    st.error("Failed to capture screenshot")
            except Exception as e:
                st.error(f"Error getting screenshot: {str(e)}")
        
        # Refresh Screenshot
        if st.button("Refresh Screenshot"):
            try:
                output_response = requests.get(f"{API_URL}/get_messages")
                if output_response.status_code == 200:
                    messages = output_response.json()
                    for msg in reversed(messages):
                        if msg.get('type') == 'screenshot':
                            screenshot_data = msg.get('image')
                            if screenshot_data:
                                img_bytes = base64.b64decode(screenshot_data)
                                img = Image.open(io.BytesIO(img_bytes))
                                st.subheader("Last Screenshot")
                                st.image(img, caption="Remote Screenshot", use_column_width=True)
                            break
                else:
                    st.error("Failed to retrieve screenshot")
            except Exception as e:
                st.error(f"Error retrieving screenshot: {str(e)}")

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
