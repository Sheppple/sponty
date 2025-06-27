import spotipy
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

# Initialize session state
if "token_info" not in st.session_state:
    st.session_state.token_info = None
if "auth_pending" not in st.session_state:
    st.session_state.auth_pending = False
if "code_used" not in st.session_state:
    st.session_state.code_used = False

# Spotify OAuth setup
auth_manager = SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE,
    show_dialog=True,
    cache_handler=None
)

# Query parameters
query_params = st.query_params

# --- Authentication Flow ---
if not st.session_state.token_info:
    if "code" in query_params and not st.session_state.code_used:
        st.session_state.auth_pending = True
        st.session_state.code_used = True
        code = query_params["code"]

        try:
            token_info = auth_manager.get_access_token(code, as_dict=True)

            if token_info:
                st.session_state.token_info = token_info
                st.session_state.auth_pending = False
                st.query_params.clear()  # ✅ new way to clear ?code
                st.rerun()
            else:
                st.error("⚠️ Failed to retrieve access token. Please log in again.")
                st.session_state.auth_pending = False
                st.stop()

        except Exception as e:
            st.error(f"❌ OAuth Error: {e}")
            st.session_state.auth_pending = False
            st.stop()

    else:
        # Not logged in
        st.title("🎧 Welcome to <sponty/>")
        auth_url = auth_manager.get_authorize_url()
        st.markdown(f"[**Login with Spotify**]({auth_url})")

        if st.button("Reset Login"):
            for key in ["token_info", "auth_pending", "code_used"]:
                st.session_state.pop(key, None)
            st.query_params.clear()
            st.rerun()

        st.stop()

if st.session_state.auth_pending:
    st.info("⏳ Finishing authentication...")
    st.stop()

if not st.session_state.token_info:
    st.error("⚠️ No token found. Please login again.")
    st.stop()

# --- Main App ---
token_info = st.session_state.token_info
sp = spotipy.Spotify(auth=token_info['access_token'])


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