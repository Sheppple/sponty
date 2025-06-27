import streamlit as st
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = "https://sponty.streamlit.app"

SCOPE = "user-top-read"

st.set_page_config(page_title="Login - Sponty")

st.title("🎧 Connect to Spotify")

if "token_info" not in st.session_state:
    auth_manager = SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
        show_dialog=True,
        cache_handler=None,
    )

    auth_url = auth_manager.get_authorize_url()
    st.markdown(f"[**Click here to login with Spotify**]({auth_url})")

    query_params = st.query_params
    if "code" in query_params:
        code = query_params["code"]
        try:
            token_info = auth_manager.get_access_token(code, as_dict=True)
            st.session_state.token_info = token_info
            st.success("Authentication successful! Redirecting to app...")
            st.switch_page("main.py")  # 👈 goes to main app page
        except Exception as e:
            st.error(f"OAuth error: {e}")

else:
    st.success("You're already logged in!")
    st.switch_page("main.py")
