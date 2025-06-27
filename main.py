import spotipy
from spotipy.cache_handler import CacheHandler
from spotipy.oauth2 import SpotifyOAuth
import streamlit as st
from dotenv import load_dotenv
import os


load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = "https://sponty.streamlit.app"
SCOPE = "user-top-read"

# Loading the CSS
with open('assets/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Page Configuration
st.set_page_config(page_title = '<sponty/>', page_icon = 'assets/sponty.svg')

# -------------------------------
# ✅ Custom Session-Based Cache Handler
# -------------------------------
class StreamlitSessionCacheHandler(CacheHandler):
    def __init__(self, session_key="token_info"):
        self.session_key = session_key

    def get_cached_token(self):
        return st.session_state.get(self.session_key, None)

    def save_token_to_cache(self, token_info):
        st.session_state[self.session_key] = token_info

# -------------------------------
# Get Spotify OAuth Auth Manager
# -------------------------------
def get_auth_manager():
    return SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
        show_dialog=True,
        cache_handler=StreamlitSessionCacheHandler() # Use the custom cache handler
    )

# -------------------------------
# Initialize Session State
# -------------------------------
# Ensure all necessary session state variables are initialized
if "token_info" not in st.session_state:
    st.session_state.token_info = None
if "auth_pending" not in st.session_state:
    st.session_state.auth_pending = False
# The `code_used` flag is crucial to prevent reprocessing the same code
if "code_used" not in st.session_state:
    st.session_state.code_used = False

query_params = st.query_params
auth_manager = get_auth_manager()

# -------------------------------
# OAuth Flow Handling
# -------------------------------
# If no token_info, attempt to authenticate
if not st.session_state.token_info:
    # Check if a 'code' parameter exists in the URL after Spotify redirect
    if "code" in query_params:
        # If code is present and hasn't been used yet in this session
        if not st.session_state.code_used:
            st.session_state.auth_pending = True
            st.session_state.code_used = True # Mark code as used for this session
            code = query_params["code"]

            try:
                # Exchange the code for an access token
                token_info = auth_manager.get_access_token(code, as_dict=True)
                if token_info:
                    st.session_state.token_info = token_info
                    st.session_state.auth_pending = False
                    # Clear query params to remove the 'code' from the URL
                    # This prevents the app from trying to re-process the code on subsequent runs
                    st.query_params.clear()
                    st.rerun() # Rerun to remove the code from the URL and display main content
                else:
                    st.error("Failed to retrieve access token. Please log in again.")
                    # Optionally clear session state here if token retrieval truly failed
                    st.session_state.clear()
                    st.query_params.clear() # Ensure clean slate
                    st.rerun() # Rerun to show login button
            except Exception as e:
                st.error(f"OAuth Error: {e}. Please try logging in again.")
                st.session_state.clear() # Clear session state on error
                st.query_params.clear() # Ensure clean slate
                st.rerun() # Rerun to show login button
        else:
            # If code is present but already used (e.g., during a rerun from code_used=True)
            # We don't need to do anything here, just let the app continue if token_info is set
            # or show the login button if not (which should be handled by the next `if` block)
            pass
    elif st.session_state.auth_pending:
        # This state is for when the code was just processed, and we are waiting for rerun
        st.info("Finishing authentication...")
        st.stop() # Stop further execution until rerun
    else:
        # Not logged in and no code in URL - show login button
        st.markdown("<div class='title'><h1>&lt;sponty/&gt</h1></div>", unsafe_allow_html=True)
        auth_url = auth_manager.get_authorize_url()
        st.markdown(
            f"""<div class="spotify_button"><a href="{auth_url}" class="spotify_login">login with Spotify</a></div>""",
            unsafe_allow_html=True
        )

        if st.button("Reset Login"):
            st.session_state.clear()
            st.query_params.clear()
            st.rerun()

        st.stop() # Stop further execution if not authenticated

# If authentication is still pending (e.g., after the initial redirect and before `st.rerun()` finishes)
if st.session_state.auth_pending:
    st.info("Finishing authentication...")
    st.stop()

# -------------------------------
# Refresh Token If Expired
# -------------------------------
# Ensure token_info exists before trying to use or refresh it
if st.session_state.token_info:
    token_info = st.session_state.token_info
    if auth_manager.is_token_expired(token_info):
        try:
            token_info = auth_manager.refresh_access_token(token_info['refresh_token'])
            if token_info:
                st.session_state.token_info = token_info
            else:
                st.error("Failed to refresh token. Please log in again.")
                st.session_state.clear()
                st.rerun()
        except Exception as e:
            st.error(f"Error refreshing token: {e}. Please log in again.")
            st.session_state.clear()
            st.rerun()
else:
    # If we somehow reached here without token_info, force a re-login
    st.session_state.clear()
    st.rerun()

# Create Spotify session only if token_info is valid
try:
    if st.session_state.token_info and 'access_token' in st.session_state.token_info:
        sp = spotipy.Spotify(auth=st.session_state.token_info['access_token'])
    else:
        # This case should ideally not be hit if the above logic works
        st.error("Authentication required. Please log in.")
        st.session_state.clear()
        st.rerun()
except Exception as e:
    st.error(f"Failed to initialize Spotify client: {e}. Please log in again.")
    st.session_state.clear()
    st.rerun()


# -------------------------------
# MAIN APP CONTENT
# -------------------------------

# Title
st.markdown("<div class='title'><h1>&lt;sponty/&gt</h1></div>", unsafe_allow_html=True)

# Time Range Selector
time_range = st.selectbox('time frame', options = ['last month >', 'last 6 months >', 'last year >'], label_visibility = 'hidden', key = 'selector')

if time_range == 'last month >':
  time_range = 'short_term'
elif time_range == 'last 6 months >':
  time_range = 'medium_term'
else:
  time_range = 'long_term'

# Top Songs
top_tracks = sp.current_user_top_tracks(limit = 10, time_range = time_range)
track_name = [track['name'] for track in top_tracks['items']]

# Top Artists
top_artists = sp.current_user_top_artists(limit = 10, time_range = time_range)
artist_name = [artist['name'] for artist in top_artists['items']]

# Main Container
container = st.container(border = True, key = 'container')

with container:
  col1, col2 = st.columns(2, gap = 'medium')

  with col1:
    top_songs_con = st.container(key = 'top_songs')
    with top_songs_con:
      st.subheader('top songs')
      for i, name in enumerate(track_name, start = 1):
        st.markdown(f"""<div style="display: flex; align-items: center; gap: 10px;"><div class="song-rank-circle">{i}</div><div>{name}</div></div>""", unsafe_allow_html=True)

  with col2:
    top_artists_con = st.container(key = 'top_artists')
    with top_artists_con:
      st.subheader('top artists')
      for i, name in enumerate(artist_name, start = 1):
        st.markdown(f"""<div style="display: flex; align-items: center; gap: 10px;"><div class="artist-rank-circle">{i}</div><div>{name}</div></div>""", unsafe_allow_html=True)

# Github Link
st.markdown("<div class='link'><p><a href = 'https://github.com/ivan-padilla/sponty' targe = '_blank' rel = 'noopener noreferrer't>&lt;github.com/&gt</a></p></div>", unsafe_allow_html=True)