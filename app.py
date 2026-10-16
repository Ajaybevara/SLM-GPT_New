import streamlit as st
import os
import base64
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Page Configuration MUST be the first Streamlit command ---
st.set_page_config(
    page_title="Drake SLM/GPT",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

def image_data_uri(path):
    """Return a local image as an inline URI so the header works everywhere."""
    with open(path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode("ascii")
    mime_type = "image/png" if path.lower().endswith(".png") else "image/jpeg"
    return f"data:{mime_type};base64,{encoded}"


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
THEME = st.query_params.get("theme", "dark")
if THEME not in {"dark", "light"}:
    THEME = "dark"

THEMES = {
    "dark": {
        "bg": "#070f1a", "header": "#06111f", "sidebar": "#081321",
        "panel": "#0b1626", "soft": "#111d2e", "border": "#263851",
        "text": "#f7f9fc", "muted": "#a8b6ca", "input": "#111d2e",
        "hover": "#1a2940", "scheme": "dark",
    },
    "light": {
        "bg": "#f4f7fb", "header": "#ffffff", "sidebar": "#ffffff",
        "panel": "#ffffff", "soft": "#edf2f8", "border": "#cbd5e1",
        "text": "#152033", "muted": "#526277", "input": "#ffffff",
        "hover": "#e2e8f0", "scheme": "light",
    },
}
palette = THEMES[THEME]
logo_name = "drake-logo-dark.png" if THEME == "dark" else "drake-logo-light.png"
LOGO_URI = image_data_uri(os.path.join(BASE_DIR, "assets", logo_name))
NEXT_THEME = "light" if THEME == "dark" else "dark"
THEME_ICON = "☀" if THEME == "dark" else "☾"
THEME_LABEL = "Switch to light mode" if THEME == "dark" else "Switch to dark mode"

st.markdown(
    f"""<style>
    :root {{
        --drake-bg: {palette['bg']};
        --drake-header: {palette['header']};
        --drake-sidebar: {palette['sidebar']};
        --drake-panel: {palette['panel']};
        --drake-panel-soft: {palette['soft']};
        --drake-border: {palette['border']};
        --drake-text: {palette['text']};
        --drake-muted: {palette['muted']};
        --drake-input: {palette['input']};
        --drake-hover: {palette['hover']};
        --drake-accent: #ef2529;
        --drake-blue: #2388d9;
    }}
    html, body, .stApp {{ color-scheme: {palette['scheme']} !important; }}
    </style>""",
    unsafe_allow_html=True,
)

st.markdown("""<style>
/* 🚀 NUKE STREAMLIT BRANDING BUT KEEP SIDEBAR TOGGLE */
.stDeployButton {display: none !important;}
[data-testid="stDecoration"] {display: none !important;}
footer {display: none !important;}

/* Hide the top-right menu but keep the toolbar for the sidebar toggle */
[data-testid="stToolbarActions"] {display: none !important;}
.stAppHeader {
    background: transparent !important;
    height: 0 !important;
    overflow: visible !important;
}

html, body, [data-testid="stAppViewContainer"], .stApp {
    background: var(--drake-bg) !important;
    color: var(--drake-text) !important;
}
body {background: var(--drake-bg) !important; color: var(--drake-text) !important;}
[data-testid="stAppViewContainer"] p,
[data-testid="stAppViewContainer"] label,
[data-testid="stAppViewContainer"] h1,
[data-testid="stAppViewContainer"] h2,
[data-testid="stAppViewContainer"] h3,
[data-testid="stAppViewContainer"] h4,
[data-testid="stAppViewContainer"] h5,
[data-testid="stAppViewContainer"] h6,
[data-testid="stAppViewContainer"] li,
[data-testid="stAppViewContainer"] span {color: var(--drake-text);}

/* Drake application header */
.drake-header {
    position: fixed;
    inset: 0 0 auto 0;
    height: 94px;
    z-index: 999990;
    display: grid;
    grid-template-columns: 250px 1fr 250px;
    align-items: center;
    padding: 0 52px;
    background: var(--drake-header);
    border-top: 7px solid #3b2930;
    border-bottom: 1px solid var(--drake-border);
    box-sizing: border-box;
}
.drake-header__logo {display: flex; align-items: center;}
.drake-header__logo img {
    width: 180px;
    height: 74px;
    object-fit: contain;
}
.drake-header__title {
    margin: 0;
    text-align: center;
    color: var(--drake-text);
    font-size: 35px;
    font-weight: 800;
    letter-spacing: .2px;
    line-height: 1;
}
.drake-header__actions {display: flex; justify-content: flex-end;}
.drake-theme-icon {
    width: 48px;
    height: 48px;
    display: grid;
    place-items: center;
    border: 1px solid var(--drake-border);
    border-radius: 13px;
    color: var(--drake-text) !important;
    background: var(--drake-panel);
    font-size: 26px;
    text-decoration: none !important;
    transition: transform .15s ease, border-color .15s ease;
}
.drake-theme-icon:hover {transform: translateY(-1px); border-color: var(--drake-accent);}

/* Leave room for the fixed header */
[data-testid="stMain"] .block-container {
    padding-top: 7.4rem !important;
    max-width: 1500px;
}

/* Left navigation panel */
section[data-testid="stSidebar"] {
    top: 94px !important;
    height: calc(100vh - 94px) !important;
    display: block !important;
    visibility: visible !important;
    width: 460px !important;
    min-width: 460px !important;
    max-width: 460px !important;
    transform: translateX(0) !important;
    left: 0 !important;
    background: var(--drake-sidebar) !important;
    border-right: 1px solid var(--drake-border);
    transition: none !important;
    animation: none !important;
}
section[data-testid="stSidebar"] > div {
    width: 100% !important;
    min-width: 0 !important;
    max-width: 460px !important;
    background: var(--drake-sidebar) !important;
    transition: none !important;
    animation: none !important;
}
[data-testid="stSidebarContent"],
[data-testid="stSidebarUserContent"],
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
    transition: none !important;
    animation: none !important;
}
section[data-testid="stSidebar"] [data-testid="stImage"] img {
    width: 150px !important;
    max-height: 78px !important;
    object-fit: contain !important;
    margin: 4px auto 12px !important;
    display: block !important;
}
section[data-testid="stSidebar"] hr {border-color: var(--drake-border) !important;}
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] h3 {color: var(--drake-text) !important;}
section[data-testid="stSidebar"] [role="radiogroup"] label {
    width: 255px !important;
    min-height: 52px !important;
    padding: 13px 16px !important;
    margin: 8px 0 !important;
    border: 1px solid transparent;
    border-radius: 8px;
    background: var(--drake-panel-soft);
    box-sizing: border-box !important;
    align-items: center !important;
}
section[data-testid="stSidebar"] [role="radiogroup"] label p,
section[data-testid="stSidebar"] [role="radiogroup"] label span {
    font-size: 16px !important;
    font-weight: 600 !important;
    line-height: 1.3 !important;
}
section[data-testid="stSidebar"] [role="radiogroup"] + div,
section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
    font-size: 16px !important;
    font-weight: 700 !important;
}
section[data-testid="stSidebar"] [role="radiogroup"] label:hover {
    border-color: #3c526f;
}
section[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
    border-color: var(--drake-accent);
    background: var(--drake-panel-soft);
}

/* Match controls and content panels to the reference styling */
[data-testid="stFileUploaderDropzone"],
[data-testid="stExpander"],
[data-testid="stForm"],
[data-testid="stChatMessage"] {
    background: var(--drake-panel-soft) !important;
    border-color: var(--drake-border) !important;
    border-radius: 10px !important;
}
input, textarea, [data-baseweb="select"] > div,
[data-testid="stChatInput"] textarea {
    background: var(--drake-input) !important;
    color: var(--drake-text) !important;
    border-color: var(--drake-border) !important;
}
[data-baseweb="popover"],
[data-baseweb="popover"] > div,
[data-baseweb="menu"],
[data-baseweb="select"] ul,
[role="listbox"] {
    background: var(--drake-panel) !important;
    border-color: var(--drake-border) !important;
    color: var(--drake-text) !important;
}
[role="option"], [data-baseweb="menu"] li {
    background: var(--drake-panel) !important;
    color: var(--drake-text) !important;
}
[role="option"] *, [data-baseweb="menu"] li * {
    color: var(--drake-text) !important;
}
[role="option"]:hover,
[role="option"][aria-selected="true"],
[data-baseweb="menu"] li:hover {
    background: var(--drake-hover) !important;
}
[data-baseweb="select"] svg,
[data-baseweb="popover"] svg {fill: var(--drake-text) !important; color: var(--drake-text) !important;}
[data-baseweb="tab-list"] {border-bottom-color: var(--drake-border) !important;}
[data-baseweb="tab"] {color: var(--drake-text) !important;}
[data-testid="stAlert"] {
    background: var(--drake-panel-soft) !important;
    color: var(--drake-text) !important;
    border-color: var(--drake-border) !important;
}
[data-testid="stBottom"],
[data-testid="stBottom"] > div,
[data-testid="stBottomBlockContainer"],
[data-testid="stChatInput"],
[data-testid="stChatInput"] > div,
.stChatFloatingInputContainer,
.stChatFloatingInputContainer > div {
    background: var(--drake-bg) !important;
    border-color: var(--drake-border) !important;
    color: var(--drake-text) !important;
}
[data-testid="stChatInput"] button,
[data-testid="stChatInput"] svg {
    color: var(--drake-text) !important;
    fill: var(--drake-text) !important;
}
[data-testid="stMarkdownContainer"] code,
[data-testid="stCodeBlock"] {
    background: var(--drake-panel-soft) !important;
    color: var(--drake-text) !important;
}
[data-testid="stDataFrame"], [data-testid="stTable"] {
    color: var(--drake-text) !important;
    background: var(--drake-panel) !important;
}
.stButton > button,
[data-testid="stButton"] button,
[data-testid="stFileUploaderDropzone"] button {
    color: var(--drake-text) !important;
    background: var(--drake-panel-soft) !important;
    -webkit-text-fill-color: var(--drake-text) !important;
}
.stButton > button *,
[data-testid="stButton"] button *,
[data-testid="stFileUploaderDropzone"] button * {
    color: var(--drake-text) !important;
    -webkit-text-fill-color: var(--drake-text) !important;
}
.stButton > button:hover,
.stButton > button:focus-visible,
[data-testid="stButton"] button:hover,
[data-testid="stButton"] button:focus-visible,
[data-testid="stFileUploaderDropzone"] button:hover,
[data-testid="stFileUploaderDropzone"] button:focus-visible {
    color: var(--drake-text) !important;
    background: var(--drake-hover) !important;
    border-color: var(--drake-accent) !important;
    box-shadow: 0 0 0 1px var(--drake-accent) !important;
}
.stButton > button:hover *,
.stButton > button:focus-visible *,
[data-testid="stButton"] button:hover *,
[data-testid="stButton"] button:focus-visible *,
[data-testid="stFileUploaderDropzone"] button:hover *,
[data-testid="stFileUploaderDropzone"] button:focus-visible * {
    color: var(--drake-text) !important;
}
.stButton > button:active,
[data-testid="stButton"] button:active,
[data-testid="stFileUploaderDropzone"] button:active {
    color: #ffffff !important;
    background: var(--drake-accent) !important;
    border-color: var(--drake-accent) !important;
}
.stButton > button:active *,
[data-testid="stButton"] button:active *,
[data-testid="stFileUploaderDropzone"] button:active * {
    color: #ffffff !important;
}
.stButton > button:disabled,
.stButton > button[disabled],
[data-testid="stButton"] button:disabled,
[data-testid="stButton"] button[disabled],
[data-testid^="stBaseButton"]:disabled {
    color: var(--drake-muted) !important;
    background: var(--drake-panel-soft) !important;
    background-color: var(--drake-panel-soft) !important;
    border-color: var(--drake-border) !important;
    -webkit-text-fill-color: var(--drake-muted) !important;
    opacity: 1 !important;
    box-shadow: none !important;
}
.stButton > button:disabled *,
.stButton > button[disabled] *,
[data-testid="stButton"] button:disabled *,
[data-testid="stButton"] button[disabled] *,
[data-testid^="stBaseButton"]:disabled * {
    color: var(--drake-muted) !important;
    -webkit-text-fill-color: var(--drake-muted) !important;
}
.stButton > button {
    border-radius: 7px !important;
    border-color: var(--drake-border) !important;
}
.stButton > button[kind="primary"] {
    background: var(--drake-accent) !important;
    border-color: var(--drake-accent) !important;
}

/* FORCE SHOW SIDEBAR TOGGLE */
[data-testid="collapsedControl"] {
    display: flex !important;
    z-index: 1000000 !important;
    visibility: visible !important;
    top: 104px !important;
}
[data-testid="stSidebarCollapseButton"] button,
[data-testid="collapsedControl"] button,
[data-testid="stExpandSidebarButton"],
[data-testid="stExpandSidebarButton"] button {
    color: var(--drake-text) !important;
    background: var(--drake-panel-soft) !important;
    border: 1px solid var(--drake-border) !important;
    border-radius: 10px !important;
}
[data-testid="stSidebarCollapseButton"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    position: fixed !important;
    top: 105px !important;
    left: calc(clamp(330px, 29vw, 520px) - 58px) !important;
    width: 44px !important;
    height: 44px !important;
    align-items: center !important;
    justify-content: center !important;
    z-index: 1000002 !important;
    pointer-events: auto !important;
    transform: none !important;
}
[data-testid="stSidebarCollapseButton"] button {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    width: 44px !important;
    height: 44px !important;
    min-width: 44px !important;
    padding: 0 !important;
    align-items: center !important;
    justify-content: center !important;
}
[data-testid="stSidebarHeader"] {
    overflow: visible !important;
    min-height: 54px !important;
}
[data-testid="stSidebarCollapseButton"] button:hover,
[data-testid="collapsedControl"] button:hover,
[data-testid="stExpandSidebarButton"]:hover,
[data-testid="stExpandSidebarButton"] button:hover {
    color: var(--drake-text) !important;
    background: var(--drake-hover) !important;
    border-color: var(--drake-accent) !important;
}
[data-testid="stSidebarCollapseButton"] svg,
[data-testid="collapsedControl"] svg,
[data-testid="stExpandSidebarButton"] svg {
    color: var(--drake-text) !important;
    fill: var(--drake-text) !important;
    stroke: var(--drake-text) !important;
}
[data-testid="stSidebarCollapseButton"] span,
[data-testid="stExpandSidebarButton"] span {
    color: var(--drake-text) !important;
    -webkit-text-fill-color: var(--drake-text) !important;
    font-size: 25px !important;
    opacity: 1 !important;
}
[data-testid="stSidebarCollapseButton"] [data-testid="stIconMaterial"],
[data-testid="stExpandSidebarButton"] [data-testid="stIconMaterial"] {
    display: inline-block !important;
    visibility: visible !important;
    opacity: 1 !important;
    color: var(--drake-text) !important;
    -webkit-text-fill-color: var(--drake-text) !important;
}
[data-testid="stExpandSidebarButton"] {
    display: flex !important;
    visibility: visible !important;
    position: fixed !important;
    top: 105px !important;
    left: 16px !important;
    width: 44px !important;
    height: 44px !important;
    align-items: center !important;
    justify-content: center !important;
    z-index: 1000001 !important;
    opacity: 1 !important;
}
[data-testid="stExpandSidebarButton"] button {
    width: 44px !important;
    height: 44px !important;
    padding: 0 !important;
}
[data-testid="stToolbar"]:has([data-testid="stExpandSidebarButton"]) {
    display: block !important;
    visibility: visible !important;
    overflow: visible !important;
    position: fixed !important;
    inset: 0 !important;
    pointer-events: none !important;
    z-index: 1000000 !important;
}
[data-testid="stToolbar"]:has([data-testid="stExpandSidebarButton"])
[data-testid="stExpandSidebarButton"] {
    pointer-events: auto !important;
}

/* Static controls sidebar: collapse, expand, and resize controls are disabled. */
[data-testid="stSidebarCollapseButton"],
[data-testid="stExpandSidebarButton"],
[data-testid="collapsedControl"],
[data-testid="stSidebarResizeHandle"] {
    display: none !important;
    visibility: hidden !important;
    opacity: 0 !important;
    pointer-events: none !important;
}

* {scrollbar-color: var(--drake-muted) var(--drake-panel) !important;}
*::-webkit-scrollbar-track {background: var(--drake-panel) !important;}
*::-webkit-scrollbar-thumb {
    background: var(--drake-muted) !important;
    border: 2px solid var(--drake-panel) !important;
    border-radius: 10px !important;
}

@media (max-width: 760px) {
    .drake-header {
        height: 78px;
        grid-template-columns: 94px minmax(0, 1fr) 46px;
        padding: 0 10px;
    }
    .drake-header__logo img {width: 92px; height: 56px;}
    .drake-header__title {font-size: clamp(19px, 6vw, 25px); white-space: nowrap;}
    .drake-theme-icon {width: 38px; height: 38px; border-radius: 10px; font-size: 21px;}

    /* Stack controls above results on narrow screens. */
    [data-testid="stAppViewContainer"] {
        display: flex !important;
        flex-direction: column !important;
        overflow-x: hidden !important;
        overflow-y: auto !important;
    }
    section[data-testid="stSidebar"] {
        position: relative !important;
        inset: auto !important;
        order: 1 !important;
        width: 100% !important;
        min-width: 100% !important;
        max-width: 100% !important;
        height: auto !important;
        max-height: none !important;
        margin-top: 78px !important;
        border-right: 0 !important;
        border-bottom: 1px solid var(--drake-border) !important;
        overflow: visible !important;
    }
    section[data-testid="stSidebar"] > div {
        width: 100% !important;
        max-width: none !important;
        height: auto !important;
        overflow: visible !important;
    }
    section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"] {
        padding: 18px 20px 24px !important;
    }
    section[data-testid="stSidebar"] [role="radiogroup"] label {
        width: 100% !important;
    }
    [data-testid="stMain"] {
        order: 2 !important;
        width: 100% !important;
        min-width: 0 !important;
        overflow: visible !important;
    }
    [data-testid="stMain"] .block-container {
        width: 100% !important;
        max-width: 100% !important;
        padding: 1.5rem 18px 7rem !important;
    }
    [data-testid="stBottom"] {width: 100% !important;}
    h1 {font-size: 1.7rem !important;}
    h2 {font-size: 1.4rem !important;}
    h3 {font-size: 1.15rem !important;}
}

@media (min-width: 761px) and (max-width: 1200px) {
    .drake-header {grid-template-columns: 190px 1fr 100px; padding: 0 26px;}
    .drake-header__logo img {width: 150px; height: 68px;}
    .drake-header__title {font-size: 29px;}
    section[data-testid="stSidebar"] {
        width: 360px !important;
        min-width: 360px !important;
        max-width: 360px !important;
    }
    section[data-testid="stSidebar"] > div {max-width: 360px !important;}
    section[data-testid="stSidebar"] [role="radiogroup"] label {width: 100% !important;}
    [data-testid="stMain"] .block-container {
        max-width: 100% !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
}

@media (min-width: 1201px) and (max-width: 1500px) {
    section[data-testid="stSidebar"] {
        width: 420px !important;
        min-width: 420px !important;
        max-width: 420px !important;
    }
    section[data-testid="stSidebar"] > div {max-width: 420px !important;}
}

/* Markdown table cells and chat placeholders have their own Streamlit colors. */
[data-testid="stMarkdownContainer"] table,
[data-testid="stMarkdownContainer"] thead,
[data-testid="stMarkdownContainer"] tbody,
[data-testid="stMarkdownContainer"] tr,
[data-testid="stMarkdownContainer"] th,
[data-testid="stMarkdownContainer"] td,
[data-testid="stMarkdownContainer"] th *,
[data-testid="stMarkdownContainer"] td * {
    color: var(--drake-text) !important;
    -webkit-text-fill-color: var(--drake-text) !important;
    border-color: var(--drake-border) !important;
}
[data-testid="stMarkdownContainer"] th {
    background: var(--drake-hover) !important;
}
[data-testid="stMarkdownContainer"] td {
    background: var(--drake-panel-soft) !important;
}
[data-testid="stMarkdownContainer"] a {
    color: var(--drake-blue) !important;
    -webkit-text-fill-color: var(--drake-blue) !important;
    text-decoration: underline;
}
input, textarea, [data-testid="stChatInput"] textarea {
    color: var(--drake-text) !important;
    -webkit-text-fill-color: var(--drake-text) !important;
    caret-color: var(--drake-text) !important;
}
input::placeholder, textarea::placeholder,
[data-testid="stChatInput"] textarea::placeholder {
    color: var(--drake-muted) !important;
    -webkit-text-fill-color: var(--drake-muted) !important;
    opacity: 1 !important;
}
[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] p {
    color: var(--drake-muted) !important;
}
/* YOUR CUSTOM CHAT & METADATA CSS */
/* ... (Keep all your chat CSS exactly the same) ... */
</style>""", unsafe_allow_html=True)

st.markdown(
    f"""
    <header class="drake-header">
        <div class="drake-header__logo"><img src="{LOGO_URI}" alt="Drake AI"></div>
        <h1 class="drake-header__title">Drake SLM/GPT</h1>
        <div class="drake-header__actions">
            <a class="drake-theme-icon" href="?theme={NEXT_THEME}" target="_self"
               title="{THEME_LABEL}" aria-label="{THEME_LABEL}">{THEME_ICON}</a>
        </div>
    </header>
    """,
    unsafe_allow_html=True,
)

# --- Constants & Configuration (ABSOLUTE PATHS FIX) ---
TEMP_DIR = os.path.join(BASE_DIR, "temp_uploads")
os.makedirs(TEMP_DIR, exist_ok=True)

# --- Database Initialization ---
from database.db_utils import (
    initialize_extended_schema, 
    get_user_vault, 
    get_document_markdown, 
    get_chat_history,
    delete_document,
    delete_chat_history
)

@st.cache_resource
def init_db():
    print("Initializing demo database schema...")
    initialize_extended_schema()
    print("System initialization complete.")
    return True

init_db()

# --- App State Management ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = True
if 'username' not in st.session_state:
    st.session_state.username = "Guest"
if 'user_id' not in st.session_state:
    st.session_state.user_id = 1
if 'current_app' not in st.session_state:
    st.session_state.current_app = "Home"
if 'is_temp_rag_chat' not in st.session_state:
    st.session_state.is_temp_rag_chat = False

# --- Main Application Router ---
def main():
    with st.sidebar:
            if not st.session_state.logged_in:
                st.markdown("### 🔐 Authentication Required")
                st.info("Please log in to access the portal.")
                
    # 2. YOUR EXISTING AUTH LOGIC
    if not st.session_state.logged_in:
        # Failsafe import for auth UI
        try:
            from components.auth_ui import render_auth_ui
        except ImportError:
            from auth_ui import render_auth_ui
        render_auth_ui()
        
    else:
        # 3. OVERWRITE THE SIDEBAR WITH THE REAL MENU AFTER LOGIN
        with st.sidebar:
            st.empty() # Clears the "Authentication Required" message
            
            # Dynamic Menu Options based on Role
            menu_options = ["Knowledge RAG", "Document Vault"]
            #if st.session_state.username == "admin":
               # menu_options.append("Admin Console 🛡️")
                
            # Apply button navigation before constructing the radio widget.
            if "pending_module" in st.session_state:
                st.session_state.module_navigation = st.session_state.pop("pending_module")
            st.session_state.current_app = st.radio(
                "📌 Select Module:",
                menu_options,
                key="module_navigation",
            )
            st.divider()
#            if st.button("🚪 Logout", use_container_width=True):
#                st.session_state.logged_in = True
#                st.session_state.username = "Guest"
#                st.session_state.user_id = 1
#                st.rerun()

        # --- 1. HOME DASHBOARD ---
        if st.session_state.current_app == "Home":
            st.title("🧠 Drake SLM/GPT")
            st.markdown("### Hackathon Prototype Dashboard")
            st.divider()
            col1, col2, col3 = st.columns(3)
            #with col1:
               # st.success("#### 📄 Universal OCR\nUpload scanned documents, invoices, or medical forms. this engine extracts data with flawless spatial accuracy.")
            #with col2:
               # st.info("#### 📚 Knowledge RAG\nUpload PDFs and Word documents. Builds a permanent, isolated  knowledge base for your account to chat with.")
            with col3:
                st.warning("#### 📂 Document Vault\nAccess your extraction history. Every document processed through OCR is permanently archived here for later retrieval.")

        # --- 2. UNIVERSAL OCR ---
        elif st.session_state.current_app == "Universal OCR":
            from modules.precision_ocr import render_ocr_app
            render_ocr_app()
            
        # --- 3. KNOWLEDGE RAG ---
        elif st.session_state.current_app == "Knowledge RAG":
            from modules.rag_chatbot import render_rag_app
            render_rag_app()

        # --- 4. DOCUMENT VAULT & KNOWLEDGE BASE ---
        elif st.session_state.current_app == "Document Vault":
            st.title("📂 Document Vault & Knowledge Base")
            st.markdown("Select previously extracted documents to combine them into your RAG Graph without re-uploading, and review past conversations.")
            st.divider()
            
            tab1, tab2 = st.tabs(["📑 Extracted Documents", "💬 Global Chat History"])
            
            with tab1:
                vault_records = get_user_vault(st.session_state.user_id)
                
                if not vault_records:
                    st.info("Your vault is currently empty. Process documents in the **Universal OCR** tab first.")
                else:
                    selected_for_permanent_rag = []
                    selected_for_temp_chat = []
                    
                    st.markdown("### 🗄️ Select Documents for your Knowledge Graph")
                    for record in vault_records:
                        doc_id, filename, category, confidence, extract_date = record
                        
                        # Expandable UI with Selectors
                        with st.expander(f"📄 {filename} | Type: {category} | Date: {extract_date[:10]}"):
                            c1, c2, c3, c4, c5 = st.columns([4, 3, 3, 3, 1])
                            with c1:
                                st.write(f"**Confidence:** {confidence}%")
                            with c2:
                                # MULTI-SELECT CHECKBOX
                                if st.checkbox("➕ Add to Permanent Graph", key=f"rag_sel_{doc_id}"):
                                    selected_for_permanent_rag.append((doc_id, filename))
                            with c3:
                                if st.checkbox("💬 Select for Temp Chat", key=f"temp_chat_sel_{doc_id}"):
                                    selected_for_temp_chat.append((doc_id, filename))
                            with c4:
                                # ACTUAL TEXT VIEWER
                                if st.button("👁️ View Extracted Text", key=f"view_{doc_id}"):
                                    st.session_state.view_doc_id = doc_id
                            with c5:
                                # DELETE BUTTON
                                if st.button("🗑️", key=f"del_{doc_id}", help="Permanently delete this document"):
                                    delete_document(doc_id, st.session_state.user_id)
                                    st.toast(f"Deleted '{filename}' successfully.")
                                    # If the deleted doc was being viewed, clear the viewer
                                    if "view_doc_id" in st.session_state and st.session_state.view_doc_id == doc_id:
                                        del st.session_state.view_doc_id
                                    st.rerun()
                    # Action Button to push straight to RAG
                    st.divider()
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if selected_for_permanent_rag:
                            if st.button(f"🧠 Load {len(selected_for_permanent_rag)} Documents into Permanent Graph", type="primary", use_container_width=True):
                                st.session_state.docs_to_rag = selected_for_permanent_rag
                                st.session_state.pending_module = "Knowledge RAG"
                                st.session_state.is_temp_rag_chat = False # Ensure permanent mode
                                st.rerun()
                    with col_b:
                        if selected_for_temp_chat:
                            if st.button(f"💬 Start Temp Chat with {len(selected_for_temp_chat)} Documents", use_container_width=True):
                                st.session_state.temp_chat_docs = selected_for_temp_chat
                                st.session_state.temp_chat_history = []
                                st.session_state.is_temp_rag_chat = True # Activate temp mode
                                st.session_state.pending_module = "Knowledge RAG"
                                st.rerun()

                    # Render Text Viewer if requested
                    if "view_doc_id" in st.session_state:
                        st.divider()
                        st.subheader("Document Content")
                        md_text = get_document_markdown(st.session_state.view_doc_id, st.session_state.user_id)
                        st.text_area("Markdown Extraction", md_text, height=300)

            with tab2:
                st.markdown("### 🗄️ Past RAG Conversations")
                # Fetching without session_id gets the whole history
                all_history = get_chat_history(st.session_state.user_id, "LightRAG")
                
                if not all_history:
                    st.info("No chat history found for the RAG application.")
                else:
                    if st.button("🗑️ Clear RAG Chat History", help="Permanently delete all RAG chat history for your account."):
                        delete_chat_history(st.session_state.user_id, "LightRAG")
                        st.toast("RAG chat history has been cleared successfully.")
                        st.rerun()
                    
                    st.divider()

                    for msg in all_history[-30:]: # Show last 30 messages
                        if msg["role"] != "system":
                            with st.chat_message(msg["role"]):
                                st.markdown(msg["content"])

        # --- 5. ADMIN CONSOLE ---
        elif st.session_state.current_app == "Admin Console 🛡️":
            from modules.admin_panel import render_admin_panel
            render_admin_panel()

if __name__ == "__main__":
    main()
