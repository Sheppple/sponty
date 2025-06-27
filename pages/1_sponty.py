import spotipy
import streamlit as st
from dotenv import load_dotenv
import os

load_dotenv()

# Loading the CSS
with open('assets/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Page Configuration
st.set_page_config(page_title = '<sponty/>', page_icon = 'assets/sponty.svg')

# Check if authenticated
if "token_info" not in st.session_state:
    st.warning("Please log in to Spotify first.")
    st.switch_page("auth.py")

# Load Spotify client
sp = spotipy.Spotify(auth=st.session_state.token_info["access_token"])


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