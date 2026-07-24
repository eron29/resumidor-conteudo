import streamlit as st

LIGHT_CSS = """
<style>
.stApp { background-color: #ffffff; color: #31333f; }
[data-testid="stSidebar"] { background-color: #f0f2f6; }
[data-testid="stHeader"] { background-color: rgba(255, 255, 255, 0); }
.stButton > button, .stDownloadButton > button {
    background-color: #f0f2f6; color: #31333f; border: 1px solid #d3d3d3;
}
[data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea {
    background-color: #ffffff; color: #31333f;
}
[data-testid="stExpander"] { background-color: #ffffff; border: 1px solid #d3d3d3; }
</style>
"""

DARK_CSS = """
<style>
.stApp { background-color: #0e1117; color: #fafafa; }
[data-testid="stSidebar"] { background-color: #161a23; }
[data-testid="stHeader"] { background-color: rgba(0, 0, 0, 0); }
.stButton > button, .stDownloadButton > button {
    background-color: #262730; color: #fafafa; border: 1px solid #3b3f4a;
}
[data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea {
    background-color: #262730; color: #fafafa;
}
[data-testid="stExpander"] { background-color: #161a23; border: 1px solid #3b3f4a; }
h1, h2, h3, h4, h5, h6, p, span, label, li { color: inherit; }
</style>
"""


def apply_theme():
    if "theme" not in st.session_state:
        st.session_state["theme"] = "light"
    st.markdown(DARK_CSS if st.session_state["theme"] == "dark" else LIGHT_CSS, unsafe_allow_html=True)


def theme_toggle_button():
    current = st.session_state.get("theme", "light")
    label = "Tema escuro" if current == "light" else "Tema claro"
    if st.sidebar.button(label, key="theme_toggle_btn"):
        st.session_state["theme"] = "dark" if current == "light" else "light"
        st.rerun()
