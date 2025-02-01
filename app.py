import streamlit as st
from st_on_hover_tabs import on_hover_tabs
from streamlit_lottie import st_lottie
from supabase import create_client
from datetime import datetime, timezone
import base64
from PIL import Image
import io
import time
import json
import requests

# ---------------------------
# Initialization & Config
# ---------------------------
supabase = create_client(
    "https://nufgpguitvkxctpagwwf.supabase.co",
    "YOUR_SUPABASE_API_KEY"  # Replace with your actual API key.
)

st.set_page_config(
    page_title="Remote Management System",
    page_icon="🖥️",
    layout="wide"
)

# Optionally load an external CSS file if available
try:
    with open("style.css") as f:
        st.markdown('<style>' + f.read() + '</style>', unsafe_allow_html=True)
except Exception:
    pass

# Inline custom CSS
st.markdown("""
<style>
    .client-card {
        background-color: #1E1E1E;
        border: 1px solid #00FF00;
        border-radius: 15px;
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
    .header-title {
        font-size: 2.5rem;
        font-weight: bold;
        color: #00FF00;
        text-align: center;
        margin-bottom: 20px;
    }
    /* Sidebar override */
    .css-1d391kg {
        background-color: #111;
    }
    /* For sidebar buttons in our on-hover tabs */
    .tabStyle {
        list-style-type: none;
        margin-bottom: 30px;
        padding-left: 30px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------
# Helper Functions
# ---------------------------
def decode_image(base64_string: str) -> Image.Image:
    try:
        img_bytes = base64.b64decode(base64_string)
        return Image.open(io.BytesIO(img_bytes))
    except Exception as e:
        st.error(f"Error decoding image: {e}")
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
        st.error(f"Error sending command: {e}")
        return False

def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# ---------------------------
# Command Function UIs (to appear in sidebar)
# ---------------------------
def ui_command_center(selected_client):
    st.subheader("Command Center")
    with st.form("command_form"):
        command = st.text_input("Enter Command", placeholder="Type your command here")
        submitted = st.form_submit_button("Execute")
        if submitted and command:
            if send_command(selected_client, f"cmd {command}"):
                st.success("Command sent successfully!")

def ui_screenshot(selected_client):
    st.subheader("Screenshot")
    if st.button("Capture Screenshot"):
        if send_command(selected_client, "get image"):
            st.success("Screenshot request sent!")
            time.sleep(2)

def ui_file_manager(selected_client):
    st.subheader("File Manager")
    fm_tabs = st.tabs(["List Files", "Download File", "Upload File"])
    with fm_tabs[0]:
        st.markdown("**List Files**")
        directory = st.text_input("Directory", value=".")
        if st.button("List Files"):
            command = f"file list {directory}"
            if send_command(selected_client, command):
                st.success("List Files command sent!")
    with fm_tabs[1]:
        st.markdown("**Download File**")
        filepath = st.text_input("File path to download")
        if st.button("Download File"):
            command = f"file get {filepath}"
            if send_command(selected_client, command):
                st.success("Download command sent! Check Message History for file data.")
    with fm_tabs[2]:
        st.markdown("**Upload File**")
        uploaded_file = st.file_uploader("Choose a file to upload")
        destination = st.text_input("Destination path on client", value="C:/destination/")
        if st.button("Upload File"):
            if uploaded_file and destination:
                file_bytes = uploaded_file.read()
                file_b64 = base64.b64encode(file_bytes).decode()
                payload = json.dumps({
                    "destination": destination + uploaded_file.name,
                    "content": file_b64
                })
                command = f"file upload {payload}"
                if send_command(selected_client, command):
                    st.success("Upload command sent!")
            else:
                st.error("Please select a file and specify a destination.")

def ui_message_history(selected_client):
    st.subheader("Message History")
    if st.button("Refresh Messages"):
        messages = supabase.table('messages')\
            .select('*')\
            .eq('client_id', selected_client)\
            .order('created_at', desc=True)\
            .limit(50)\
            .execute()
        for msg in messages.data:
            with st.expander(f"{msg['type'].upper()} - {msg['created_at']}", expanded=False):
                if msg['type'] == 'text':
                    st.code(msg['content'], language='bash')
                elif msg['type'] == 'image':
                    img = decode_image(msg['content'])
                    if img:
                        st.image(img)
                elif msg['type'] == 'file':
                    try:
                        file_info = json.loads(msg['content'])
                        filename = file_info.get("filename", "downloaded_file")
                        file_b64 = file_info.get("content", "")
                        file_bytes = base64.b64decode(file_b64)
                        st.download_button("Download File", file_bytes, file_name=filename)
                    except Exception as e:
                        st.error(f"Error processing file message: {e}")
                st.text(f"Status: {msg['status']}")

# ---------------------------
# Main UI: Sidebar with Client Selection and Commands
# ---------------------------
# Sidebar – Client Selector
with st.sidebar:
    st.markdown("<div class='header-title'>Remote Management</div>", unsafe_allow_html=True)
    
    # Retrieve all clients from Supabase
    clients_response = supabase.table('clients').select('*').order('last_seen', desc=True).execute()
    if clients_response.data:
        client_options = {
            f"{c['hostname']} ({c['client_id']})": c['client_id'] for c in clients_response.data
        }
        selected_client = st.selectbox("Select Client", options=list(client_options.keys()))
        selected_client_id = client_options[selected_client]
        
        # On Hover Tabs for command functions
        nav = on_hover_tabs(
            tabName=['Command', 'Screenshot', 'Files', 'History'],
            iconName=['terminal', 'camera', 'folder', 'clock'],
            default_choice=0,
            styles={
                'navtab': {
                    'background-color': '#111',
                    'color': '#818181',
                    'font-size': '18px',
                    'transition': '.3s',
                    'white-space': 'nowrap',
                    'text-transform': 'uppercase'
                },
                'tabOptionsStyle': {':hover :hover': {'color': 'red', 'cursor': 'pointer'}},
                'iconStyle': {'position': 'fixed', 'left': '7.5px', 'text-align': 'left'},
                'tabStyle': {'list-style-type': 'none', 'margin-bottom': '30px', 'padding-left': '30px'}
            },
            key="main_nav"
        )
        
        # Render the corresponding command function UI in the sidebar
        st.markdown("---")
        if nav == "Command":
            ui_command_center(selected_client_id)
        elif nav == "Screenshot":
            ui_screenshot(selected_client_id)
        elif nav == "Files":
            ui_file_manager(selected_client_id)
        elif nav == "History":
            ui_message_history(selected_client_id)
    else:
        st.warning("No clients connected.")

# ---------------------------
# Main Area (optional info or blank)
# ---------------------------
st.markdown("<div class='header-title'>Remote Management System</div>", unsafe_allow_html=True)
st.write("Use the sidebar to select a client and perform commands.")
