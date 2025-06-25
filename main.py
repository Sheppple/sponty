import spotipy
from spotipy.oauth2 import SpotifyOAuth
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()

CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
REDIRECT_URI = 'http://127.0.0.1:8000/callback'

sp = spotipy.Spotify(
  auth_manager=SpotifyOAuth(
    client_id = CLIENT_ID,
    client_secret = CLIENT_SECRET,
    redirect_uri = REDIRECT_URI,
    scope = 'user-top-read'
  )
)

st.set_page_config(page_title = 'Spotify Dashboard', page_icon = ':musical_note:')
st.title('Sponty')
st.write('Discover top songs and artists')

time_range = 'long_term'

top_tracks = sp.current_user_top_tracks(limit = 10, time_range = time_range)
track_name = [track['name'] for track in top_tracks['items']]

top_artists = sp.current_user_top_artists(limit = 10, time_range = time_range)
artist_name = [artist['name'] for artist in top_artists['items']]

st.subheader('Top Songs')
for i, name in enumerate(track_name, start = 1):
  st.write(i, name)

st.subheader('Top Artists')
for i, name in enumerate(artist_name, start = 1):
  st.write(i, name)