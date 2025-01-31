import streamlit as st
import requests
from PIL import Image
import io
import base64
from datetime import datetime

def decode_image(base64_string):
    img_bytes = base64.b64decode(base64_string)
    return Image.open(io.BytesIO(img_bytes))

st.set_page_config(page_title="Message Center", page_icon="💬")

def main():
    st.title("Message Center")
    
    # API Configuration
    api_url = "https://gamkertestbot.onrender.com"
    
    # Message sender section
    st.header("Send Message")
    
    # Text input
    message = st.text_input("Enter message ('get image' for image, 'hi' for greeting)")
    if st.button("Send"):
        if message:
            response = requests.post(
                f"{api_url}/send_message",
                json={"message": message, "type": "text"}
            )
            if response.status_code == 200:
                st.success("Message sent!")
            else:
                st.error("Failed to send message")
    
    # Message display section
    st.header("Messages and Images")
    if st.button("Refresh") or True:  # Auto-refresh
        response = requests.get(f"{api_url}/get_messages")
        if response.status_code == 200:
            messages = response.json()
            for msg in reversed(messages):  # Show newest first
                with st.container():
                    st.write(f"Time: {datetime.fromtimestamp(msg['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}")
                    
                    if msg['type'] == 'text':
                        st.write(f"Message: {msg['message']}")
                    elif msg['type'] == 'image':
                        st.write("Received Image:")
                        try:
                            img = decode_image(msg['image'])
                            st.image(img)
                        except Exception as e:
                            st.error(f"Error displaying image: {str(e)}")
                    
                    st.divider()

if __name__ == "__main__":
    main()
