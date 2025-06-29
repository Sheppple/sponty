import pylast as pl
import streamlit as st
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv('API_KEY')
API_SECRET = os.getenv('API_SECRET')

network = pl.LastFMNetwork(api_key = API_KEY, api_secret = API_SECRET)

# Loading the CSS
with open('assets/style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Page Configuration
st.set_page_config(page_title = '<sponty/>', page_icon = 'assets/sponty.svg')

# Title
st.markdown("<div class='title'><h1>&lt;sponty/&gt</h1></div>", unsafe_allow_html=True)

# Username
username = st.text_input(label = 'username', placeholder = 'Username', label_visibility= 'hidden', key = 'username')

if username:
    try:

        user = network.get_user(username)

        # Time Range Selector
        period = st.selectbox('period', options = ['last 7 days', 'last month', 'last 3 months', 'last 6 months', 'last year', 'overall'], label_visibility = 'hidden', key = 'selector')

        if period == 'last 7 days':
            period = '7day'
        if period == 'last month':
            period = '1month'
        if period == 'last 3 months':
            period = '3month'
        if period == 'last 6 months':
            period = '6month'
        if period == 'last year':
            period = '12month'


        # Top Songs
        top_tracks = user.get_top_tracks(period = period, limit = 10)
        track_name = [track.item.title for track in top_tracks]

        # Top Artists
        top_artists = user.get_top_artists(period = period, limit = 10)
        artist_name = [artist.item.name for artist in top_artists]

        # Top Albums
        top_albums = user.get_top_albums(period = period, limit = 10)
        album_name = [album.item.title for album in top_albums]
        album_artist = [album.item.artist.name for album in top_albums]
        #album = pl.Album(title = album_name, artist = album_artist, network = network)
        #album_cover = album.get_cover_image(size = 0)


        # Main Container
        container = st.container(key = 'container')

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

            top_albums_con = st.container(key = 'top_albums')

            with top_albums_con:
                st.subheader('top albums')
                cols = st.columns(5, gap = 'small')
                for i, (album, artist) in enumerate(zip(album_name, album_artist)):
                    col = cols[i % 5]
                    with col:
                        album_con = st.container(key = f"album_{i+1}")
                        with album_con:
                            cover = pl.Album(title = album, artist = artist, network = network).get_cover_image(size=2)
                            st.markdown(f"""<div style="text-align: center;"><img src="{cover}" width="125" style="border-radius: 8px;" /><div class="album_rank">{i+1}. {album}</div></div>""",unsafe_allow_html=True)

        # Github Link
        st.markdown("<div class='link'><p><a href = 'https://github.com/ivan-padilla/sponty' targe = '_blank' rel = 'noopener noreferrer't>&lt;github.com/&gt</a></p></div>", unsafe_allow_html=True)

    except pl.PyLastError:
        st.error('Username invalid.')