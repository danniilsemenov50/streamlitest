import streamlit as st
import extra_streamlit_components as stx
from supabase import create_client
from datetime import datetime, timezone
import base64
from PIL import Image
import io
import time

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
    /* Authentication styles */
    .auth-form {
        max-width: 400px;
        margin: auto;
        padding: 20px;
    }
    .auth-container {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 80vh;
    }
    
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

# Session State Initialization
def init_session_state():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'login'

# Authentication Functions
def login_user(email: str, password: str) -> bool:
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        st.session_state.user = response.user
        st.session_state.authenticated = True
        return True
    except Exception as e:
        st.error(f"Login failed: {str(e)}")
        return False

def register_user(email: str, password: str, confirm_password: str) -> bool:
    if password != confirm_password:
        st.error("Passwords do not match")
        return False
    
    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        st.success("Registration successful! Please check your email to verify your account.")
        return True
    except Exception as e:
        st.error(f"Registration failed: {str(e)}")
        return False

def logout_user():
    try:
        supabase.auth.sign_out()
        st.session_state.authenticated = False
        st.session_state.user = None
        st.experimental_rerun()
    except Exception as e:
        st.error(f"Logout failed: {str(e)}")

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
            "user_id": st.session_state.user.id
        }
        supabase.table('messages').insert(data).execute()
        return True
    except Exception as e:
        st.error(f"Error sending command: {str(e)}")
        return False

# Page Components
def render_login_page():
    st.markdown("<div class='auth-container'>", unsafe_allow_html=True)
    with st.form("login_form", clear_on_submit=True):
        st.title("🔐 Login")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.form_submit_button("Login"):
            if login_user(email, password):
                st.success("Login successful!")
                st.session_state.current_page = 'dashboard'
                st.experimental_rerun()
    
    if st.button("Need an account? Register here"):
        st.session_state.current_page = 'register'
        st.experimental_rerun()
    st.markdown("</div>", unsafe_allow_html=True)

def render_register_page():
    st.markdown("<div class='auth-container'>", unsafe_allow_html=True)
    with st.form("register_form", clear_on_submit=True):
        st.title("📝 Register")
        email = st.text_input("Email", key="register_email")
        password = st.text_input("Password", type="password", key="register_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
        
        if st.form_submit_button("Register"):
            if register_user(email, password, confirm_password):
                st.session_state.current_page = 'login'
                st.experimental_rerun()
    
    if st.button("Already have an account? Login here"):
        st.session_state.current_page = 'login'
        st.experimental_rerun()
    st.markdown("</div>", unsafe_allow_html=True)

def render_dashboard():
    # Sidebar
    with st.sidebar:
        st.title("Navigation")
        if st.button("Logout"):
            logout_user()
        
        # Get all clients for current user
        clients = supabase.table('clients')\
            .select('*')\
            .eq('user_id', st.session_state.user.id)\
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
            uploaded_file = st.file_uploader("Upload File", type=['txt', 'pdf', 'zip'])
            if uploaded_file is not None:
                if st.button("Send File"):
                    # Add file transfer logic here
                    st.info("File transfer feature coming soon!")
        
        # Message History
        with tabs[3]:
            st.header("Message History")
            if st.button("Refresh Messages"):
                messages = supabase.table('messages')\
                    .select('*')\
                    .eq('client_id', selected_client)\
                    .eq('user_id', st.session_state.user.id)\
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
                        st.text(f"Status: {msg['status']}")

def main():
    init_session_state()
    
    if not st.session_state.authenticated:
        if st.session_state.current_page == 'register':
            render_register_page()
        else:
            render_login_page()
    else:
        render_dashboard()

if __name__ == "__main__":
    main()
